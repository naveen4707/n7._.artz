"""
LOOMIS AI — MEMBER 2: GRAPHITE RENDERER
STAGE 10: EYEBROW CONSTRUCTION

Deterministic graphite construction renderer.
Constructs the planar eyebrow masses and supraorbital brow ridge:
  - Preserves validated Loomis foundation (Stages 1–7)
  - Preserves clean eyeball and eyelid construction (Stage 9)
  - Glabella keystone plane connecting the inner brow heads to the nasal root
  - Confirmed structural lower brow arch contour
  - Upper arch curvature following supraorbital margin
  - Central brow ridge flow spine
  - Clean anatomical tail convergence toward the temple

Avoids awkward hatching, comb stripes, or wireframe noise.
No external image-generation API or key is used.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter

from hand_drawn_renderer import (
    HandDrawnLoomisRenderer,
    GraphiteStrokeEngine,
    point_xy as base_point_xy,
)
from stage_09_eye_eyelid_construction import Stage09EyeRenderer


# ============================================================
# PATHS AND STAGE CONFIGURATION
# ============================================================

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = AI_ENGINE_DIR / "output"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_10.png"

STAGE_NUMBER = 10
STAGE_NAME = "Eyebrow Construction"

Point = Tuple[float, float]


# ============================================================
# STAGE 10 RENDERER
# ============================================================

class Stage10EyebrowRenderer:
    """
    Stage 10: Eyebrow Construction.

    Builds upon Stage 9 (clean eyes and Loomis foundation) by adding
    anatomical planar eyebrow masses and the glabella keystone.
    """

    def __init__(self, construction: Dict[str, Any]):
        self.construction = construction
        self.base = HandDrawnLoomisRenderer(construction)
        self.stage9 = Stage09EyeRenderer(construction)

        self.face = construction.get("accurateFace", {})
        self.eyebrows = self.face.get("eyebrows", {})
        self.loomis = construction.get("loomis", {})
        self.eye_plane = self.loomis.get("eyePlane", {})

    def get_brow_points(self, side: str) -> Optional[Dict[str, List[Point]]]:
        """
        Extract transformed lower and upper eyebrow contour points.
        MediaPipe eyebrow landmarks:
          - First 5 points: lower contour (tail to head)
          - Next 5 points: upper contour (tail to head)
        """
        group = self.eyebrows.get(side)
        if not isinstance(group, dict):
            return None

        raw_points = group.get("points", [])
        if len(raw_points) < 10:
            return None

        canvas_points: List[Point] = []
        for p in raw_points:
            pt = base_point_xy(p)
            if pt is not None:
                transformed = self.base.transform_point(pt)
                if transformed is not None:
                    canvas_points.append(transformed)

        if len(canvas_points) < 10:
            return None

        return {
            "lower": canvas_points[:5],
            "upper": canvas_points[5:],
        }

    def draw_glabella_keystone(
        self,
        engine: GraphiteStrokeEngine,
        right_brow: Dict[str, List[Point]],
        left_brow: Dict[str, List[Point]],
    ) -> None:
        """
        Draw the classic Loomis glabella keystone plane connecting
        the inner brow heads across the forehead above the nasal root.
        """
        r_head_low = right_brow["lower"][4]
        l_head_low = left_brow["lower"][4]
        r_head_up = right_brow["upper"][4]
        l_head_up = left_brow["upper"][4]

        # Keystone lateral boundary planes
        engine.quality.ghost_stroke([r_head_up, r_head_low], strength=0.22, width=0.65)
        engine.quality.ghost_stroke([l_head_up, l_head_low], strength=0.22, width=0.65)

        # Keystone upper forehead wedge
        engine.quality.ghost_stroke([r_head_up, l_head_up], strength=0.20, width=0.65)

        # Downward plane transition toward nasal root
        mid_low = (
            (r_head_low[0] + l_head_low[0]) * 0.5,
            (r_head_low[1] + l_head_low[1]) * 0.5 + 8.0,
        )
        engine.quality.ghost_stroke([r_head_low, mid_low, l_head_low], strength=0.20, width=0.65)

    def draw_eyebrow_mass(
        self,
        engine: GraphiteStrokeEngine,
        brow_data: Dict[str, List[Point]],
        side: str,
    ) -> None:
        """
        Draw clean, structural planar eyebrow mass for one side.
        Avoids noisy comb-like stripes or mechanical hatching.
        """
        lower = brow_data["lower"]
        upper = brow_data["upper"]

        # 1. Structural lower contour (core definition of eyebrow arch)
        engine.quality.structural_stroke(lower, strength=0.82, width=1.15)

        # 2. Upper arch contour following the supraorbital bone
        engine.quality.construction_stroke(upper, strength=0.60, width=0.90)

        # 3. Outer tail clean anatomical convergence
        engine.quality.structural_stroke([upper[0], lower[0]], strength=0.70, width=0.95)

        # 4. Inner head closure guide
        engine.quality.construction_stroke([upper[4], lower[4]], strength=0.45, width=0.75)

        # 5. Central brow ridge flow spine (longitudinal bone crest)
        mid_spine: List[Point] = []
        for i in range(5):
            mid_spine.append((
                (lower[i][0] + upper[i][0]) * 0.5,
                (lower[i][1] + upper[i][1]) * 0.5,
            ))
        engine.quality.ghost_stroke(mid_spine, strength=0.30, width=0.70)

    def render(self) -> Image.Image:
        """
        Render Stage 10 portrait construction page.
        Builds progressively on Stage 9 eyes and Loomis foundation.
        """
        # 1. Create fresh canvas
        image = self.base.create_canvas()

        # 2. Create unified stroke engine
        engine = GraphiteStrokeEngine(
            image,
            seed=100 + STAGE_NUMBER,
            stage_number=STAGE_NUMBER,
        )

        # 3. Draw standard stage header
        self.base.draw_header(
            engine.draw,
            STAGE_NUMBER,
            STAGE_NAME,
        )

        # 4. Rebuild validated Loomis foundation (Stages 1–7)
        self.base.draw_cranium(engine)
        self.base.draw_center_axis(engine)
        self.base.draw_eye_plane(engine)
        self.base.draw_jaw(engine)
        self.base.draw_nose(engine)
        self.base.draw_mouth(engine)
        self.base.draw_eyes(engine)
        self.base.draw_eyebrows(engine)

        # 5. Draw clean Stage 9 eyes
        alpha = float(self.eye_plane.get("angle", 0.0))
        nx = math.sin(math.radians(alpha))
        ny = -math.cos(math.radians(alpha))

        for side in ("right", "left"):
            edata = self.stage9.get_eye_side_data(side)
            if edata is not None:
                self.stage9.draw_clean_eye(engine, edata, nx, ny, alpha)

        # 6. Draw Stage 10 eyebrow construction
        r_brow = self.get_brow_points("right")
        l_brow = self.get_brow_points("left")

        if r_brow and l_brow:
            self.draw_glabella_keystone(engine, r_brow, l_brow)

        if r_brow:
            self.draw_eyebrow_mass(engine, r_brow, "right")

        if l_brow:
            self.draw_eyebrow_mass(engine, l_brow, "left")

        # 7. Apply graphite surface treatment and smoothing once
        final_image = engine.finalize()
        final_image = final_image.filter(
            ImageFilter.GaussianBlur(radius=0.10)
        )

        return final_image

    def save(self, output_path: Optional[Path] = None) -> Path:
        """Render and save Stage 10 PNG image."""
        if output_path is None:
            output_path = DEFAULT_OUTPUT

        output_path = Path(output_path)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)

        image = self.render()
        image.save(output_path, quality=95)

        return output_path


# Backward compatibility alias
Stage10EyebrowConstruction = Stage10EyebrowRenderer


# ============================================================
# CLI AND HELPERS
# ============================================================

def load_construction(path: Optional[Path] = None) -> Dict[str, Any]:
    if path is None:
        path = CONSTRUCTION_FILE

    path = Path(path)
    if not path.is_absolute():
        path = Path.cwd() / path

    if not path.exists():
        raise FileNotFoundError(
            f"Construction file not found: {path}\n"
            "Run construction_main.py first."
        )

    with path.open("r", encoding="utf-8") as f:
        construction = json.load(f)

    return construction


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Loomis AI - Stage 10 Eyebrow Construction"
    )

    parser.add_argument(
        "--input",
        default=str(CONSTRUCTION_FILE),
        help="Path to construction.json.",
    )

    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output PNG path.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    construction_path = Path(args.input)
    output_path = Path(args.output)

    if not construction_path.is_absolute():
        construction_path = Path.cwd() / construction_path

    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    print("=" * 62)
    print("LOOMIS AI / STAGE 10 / EYEBROW CONSTRUCTION")
    print("=" * 62)
    print(f"Construction: {construction_path}")
    print(f"Output:       {output_path}\n")

    construction = load_construction(construction_path)
    renderer = Stage10EyebrowRenderer(construction)

    saved_path = renderer.save(output_path)

    print("=" * 62)
    print("SUCCESS")
    print("=" * 62)
    print(f"\nStage 10 created:\n{saved_path.resolve()}\n")
    print("Added:")
    print("  [OK] Loomis foundation & clean eye construction preserved")
    print("  [OK] Glabella keystone planes between eyebrows")
    print("  [OK] Structural lower eyebrow arch contour")
    print("  [OK] Upper eyebrow arch following supraorbital margin")
    print("  [OK] Central brow ridge flow spine")
    print("  [OK] Clean outer tail anatomical convergence")
    print("=" * 62)


if __name__ == "__main__":
    main()
