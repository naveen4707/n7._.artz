"""
LOOMIS AI
MEMBER 2 - GRAPHITE QUALITY ENGINE
M2.2

Adds natural graphite/pencil characteristics to deterministic
construction geometry without modifying the underlying geometry.

This module is intentionally independent from Member 1.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFilter


Point = Tuple[float, float]


@dataclass
class GraphiteStyle:
    """
    Controls the visual character of the pencil.
    """

    # Main graphite darkness
    dark: Tuple[int, int, int] = (55, 54, 51)

    # Medium construction graphite
    medium: Tuple[int, int, int] = (90, 88, 84)

    # Light construction graphite
    light: Tuple[int, int, int] = (145, 142, 136)

    # Very light exploratory marks
    ghost: Tuple[int, int, int] = (190, 187, 181)

    # Base stroke width
    width: float = 1.15

    # Randomness of the hand
    wobble: float = 0.55

    # Number of graphite passes
    passes: int = 3

    # Paper grain strength
    grain_strength: int = 7


class GraphiteQualityEngine:
    """
    Pencil/graphite rendering layer.

    The important design principle is:

        geometry remains exact
        visual appearance becomes organic
    """

    def __init__(
        self,
        image: Image.Image,
        seed: int = 42,
        style: GraphiteStyle | None = None,
    ):
        self.image = image.convert("RGB")
        self.draw = ImageDraw.Draw(self.image)
        self.random = random.Random(seed)
        self.style = style or GraphiteStyle()

    # ---------------------------------------------------------
    # RANDOM HELPERS
    # ---------------------------------------------------------

    def _noise(self, amount: float) -> float:
        return self.random.uniform(-amount, amount)

    def _clamp(self, value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    # ---------------------------------------------------------
    # POINT PROCESSING
    # ---------------------------------------------------------

    def _jitter_point(
        self,
        point: Point,
        amount: float,
    ) -> Point:

        x, y = point

        return (
            x + self._noise(amount),
            y + self._noise(amount),
        )

    def _jitter_path(
        self,
        points: Sequence[Point],
        amount: float,
    ) -> List[Point]:

        if not points:
            return []

        result = []

        for point in points:
            result.append(
                self._jitter_point(point, amount)
            )

        return result

    # ---------------------------------------------------------
    # COLOR
    # ---------------------------------------------------------

    def _graphite_color(
        self,
        base: Tuple[int, int, int],
        variation: int = 8,
    ) -> Tuple[int, int, int]:

        result = []

        for channel in base:
            value = channel + self.random.randint(
                -variation,
                variation,
            )

            result.append(
                int(self._clamp(value, 0, 255))
            )

        return tuple(result)

    # ---------------------------------------------------------
    # PENCIL STROKE
    # ---------------------------------------------------------

    def pencil_stroke(
        self,
        points: Sequence[Point],
        *,
        strength: float = 1.0,
        width: float | None = None,
        wobble: float | None = None,
        passes: int | None = None,
        closed: bool = False,
    ) -> None:
        """
        Draw a natural graphite stroke.

        The original geometry is never modified permanently.
        Each visible pass receives only a tiny visual deviation.
        """

        if len(points) < 2:
            return

        width = width or self.style.width
        wobble = (
            self.style.wobble
            if wobble is None
            else wobble
        )

        passes = (
            self.style.passes
            if passes is None
            else passes
        )

        strength = self._clamp(
            strength,
            0.05,
            1.0,
        )

        # Main pencil passes
        for pass_index in range(passes):

            pass_factor = 1.0

            if pass_index == 0:
                pass_factor = 0.90

            elif pass_index == 1:
                pass_factor = 0.55

            else:
                pass_factor = 0.30

            jitter = wobble * (
                1.0 + pass_index * 0.45
            )

            path = self._jitter_path(
                points,
                jitter,
            )

            if closed and len(path) > 2:
                path = list(path) + [path[0]]

            base = self.style.dark

            # Lighter passes are used to simulate graphite buildup.
            if strength < 0.45:
                base = self.style.light

            elif strength < 0.70:
                base = self.style.medium

            color = self._graphite_color(
                base,
                variation=6,
            )

            alpha_strength = (
                strength
                * pass_factor
            )

            # PIL RGB drawing has no alpha.
            # Simulate pressure through lighter/darker colors.
            if alpha_strength < 0.35:
                color = self._graphite_color(
                    self.style.ghost,
                    variation=5,
                )

            elif alpha_strength < 0.65:
                color = self._graphite_color(
                    self.style.medium,
                    variation=6,
                )

            line_width = max(
                1,
                int(
                    width
                    * (
                        0.75
                        + strength * 0.55
                    )
                ),
            )

            self.draw.line(
                path,
                fill=color,
                width=line_width,
                joint="curve",
            )

        # Small graphite irregularities.
        self._add_stroke_texture(
            points,
            strength=strength,
        )

    # ---------------------------------------------------------
    # STROKE TEXTURE
    # ---------------------------------------------------------

    def _add_stroke_texture(
        self,
        points: Sequence[Point],
        *,
        strength: float,
    ) -> None:

        if len(points) < 2:
            return

        # Keep texture subtle.
        count = max(
            1,
            int(len(points) * 0.10),
        )

        for _ in range(count):

            point = self.random.choice(
                list(points)
            )

            x, y = point

            offset_x = self._noise(1.5)
            offset_y = self._noise(1.5)

            radius = self.random.choice(
                [0, 0, 1]
            )

            color = self._graphite_color(
                self.style.medium,
                variation=10,
            )

            self.draw.ellipse(
                (
                    x + offset_x - radius,
                    y + offset_y - radius,
                    x + offset_x + radius,
                    y + offset_y + radius,
                ),
                fill=color,
            )

    # ---------------------------------------------------------
    # LIGHT CONSTRUCTION STROKE
    # ---------------------------------------------------------

    def construction_stroke(
        self,
        points: Sequence[Point],
        *,
        strength: float = 0.35,
        width: float = 0.9,
        closed: bool = False,
    ) -> None:

        self.pencil_stroke(
            points,
            strength=strength,
            width=width,
            wobble=0.35,
            passes=2,
            closed=closed,
        )

    # ---------------------------------------------------------
    # IMPORTANT STRUCTURAL STROKE
    # ---------------------------------------------------------

    def structural_stroke(
        self,
        points: Sequence[Point],
        *,
        strength: float = 0.90,
        width: float = 1.25,
        closed: bool = False,
    ) -> None:

        self.pencil_stroke(
            points,
            strength=strength,
            width=width,
            wobble=0.42,
            passes=4,
            closed=closed,
        )

    # ---------------------------------------------------------
    # GHOST / SEARCHING STROKES
    # ---------------------------------------------------------

    def ghost_stroke(
        self,
        points: Sequence[Point],
        *,
        strength: float = 0.18,
        width: float = 0.65,
        closed: bool = False,
    ) -> None:

        self.pencil_stroke(
            points,
            strength=strength,
            width=width,
            wobble=0.75,
            passes=2,
            closed=closed,
        )

    # ---------------------------------------------------------
    # ELLIPSE
    # ---------------------------------------------------------

    def pencil_ellipse(
        self,
        bbox: Tuple[float, float, float, float],
        *,
        strength: float = 0.45,
        width: float = 0.9,
        passes: int = 3,
    ) -> None:

        x1, y1, x2, y2 = bbox

        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        rx = abs(x2 - x1) / 2.0
        ry = abs(y2 - y1) / 2.0

        points: List[Point] = []

        samples = 96

        for i in range(samples):

            angle = (
                2.0
                * math.pi
                * i
                / samples
            )

            x = cx + rx * math.cos(angle)
            y = cy + ry * math.sin(angle)

            points.append((x, y))

        self.pencil_stroke(
            points,
            strength=strength,
            width=width,
            wobble=0.40,
            passes=passes,
            closed=True,
        )

    # ---------------------------------------------------------
    # CROSS-CONSTRUCTION
    # ---------------------------------------------------------

    def construction_axis(
        self,
        start: Point,
        end: Point,
        *,
        strength: float = 0.28,
        width: float = 0.75,
    ) -> None:

        self.construction_stroke(
            [start, end],
            strength=strength,
            width=width,
        )

    # ---------------------------------------------------------
    # PAPER GRAIN
    # ---------------------------------------------------------

    def add_paper_grain(
        self,
        strength: int | None = None,
    ) -> Image.Image:

        strength = (
            self.style.grain_strength
            if strength is None
            else strength
        )

        width, height = self.image.size

        grain = Image.new(
            "RGB",
            (width, height),
            (247, 246, 242),
        )

        grain_draw = ImageDraw.Draw(grain)

        # Sparse microscopic graphite/paper variation.
        sample_count = int(
            width * height * 0.006
        )

        for _ in range(sample_count):

            x = self.random.randrange(width)
            y = self.random.randrange(height)

            value = self.random.randint(
                235,
                252,
            )

            grain_draw.point(
                (x, y),
                fill=(value, value, value),
            )

        grain = grain.filter(
            ImageFilter.GaussianBlur(0.25)
        )

        # Very subtle blend.
        self.image = Image.blend(
            self.image,
            grain,
            strength / 100.0,
        )

        self.draw = ImageDraw.Draw(
            self.image
        )

        return self.image

    # ---------------------------------------------------------
    # GRAPHITE DUST
    # ---------------------------------------------------------

    def add_graphite_dust(
        self,
        *,
        density: float = 0.002,
    ) -> Image.Image:

        width, height = self.image.size

        count = int(
            width
            * height
            * density
        )

        for _ in range(count):

            x = self.random.randint(
                20,
                max(20, width - 20),
            )

            y = self.random.randint(
                20,
                max(20, height - 20),
            )

            radius = self.random.choice(
                [0, 0, 0, 1]
            )

            shade = self.random.randint(
                150,
                210,
            )

            self.draw.ellipse(
                (
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                ),
                fill=(
                    shade,
                    shade,
                    shade,
                ),
            )

        return self.image

    # ---------------------------------------------------------
    # FINALIZATION
    # ---------------------------------------------------------

    def finalize(self) -> Image.Image:
        """
        Apply the subtle paper/graphite finish.
        """

        self.add_paper_grain(
            self.style.grain_strength
        )

        return self.image