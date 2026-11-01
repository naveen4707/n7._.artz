"""
LOOMIS AI — MEMBER 2: GRAPHITE RENDERER
STAGE 11: NOSE REFINEMENT

Deterministic graphite construction renderer.
Constructs the planar nose anatomy according to Loomis methodology:
  - Preserves validated Loomis foundation (Stages 1–7)
  - Preserves clean eye construction (Stage 9)
  - Preserves eyebrow and glabella construction (Stage 10)
  - Nasal dorsal ridge (central bridge spine)
  - Lateral side plane guide lines
  - Spherical ball of the nose construction
  - Left and right alar wing curves (nostril flares)
  - Under-plane of the nose (columella and nasal base)
  - Dark graphite nostril accents

Avoids awkward, cluttered wireframes or excessive hatching.
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
from stage_08_eye_construction import rotate_ellipse
from stage_10_eyebrow_construction import Stage10EyebrowRenderer


# ============================================================
# PATHS AND STAGE CONFIGURATION
# ============================================================

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = AI_ENGINE_DIR / "output"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_11.png"

STAGE_NUMBER = 11
STAGE_NAME = "Nose Refinement"

Point = Tuple[float, float]


# ============================================================
# STAGE 11 RENDERER
# ============================================================

class Stage11NoseRenderer:
    """
    Stage 11: Nose Refinement.

    Progressively advances the portrait by adding anatomical nose
    construction grounded in accurateFace.nose landmarks and Loomis planes.
    """

    def __init__(self, construction: Dict[str, Any]):
        self.construction = construction
        self.base = HandDrawnLoomisRenderer(construction)
        self.stage10 = Stage10EyebrowRenderer(construction)

        self.face = construction.get("accurateFace", {})
        self.nose = self.face.get("nose", {})
        self.loomis = construction.get("loomis", {})
        self.eye_plane = self.loomis.get("eyePlane", {})

    def draw_nose_construction(
        self,
        engine: GraphiteStrokeEngine,
        alpha: float,
    ) -> None:
        """
        Draw clean, anatomical nose construction:
          - Dorsal bridge line
          - Lateral side planes
          - Ball of the nose sphere
          - Alar wing flares
          - Under-plane and nostril accents
        """
        scale = self.base.transform["scale"]

        tip_dict = self.nose.get("tip")
        if not tip_dict:
            return

        tip_pt = self.base.transform_point(base_point_xy(tip_dict))
        if tip_pt is None:
            return

        bridge_raw = self.nose.get("bridge", [])
        bridge_pts: List[Point] = []
        for p in bridge_raw:
            pt = self.base.transform_point(base_point_xy(p))
            if pt is not None:
                bridge_pts.append(pt)

        lower_raw = self.nose.get("lowerContour", [])
        lower_pts: List[Point] = []
        for p in lower_raw:
            pt = self.base.transform_point(base_point_xy(p))
            if pt is not None:
                lower_pts.append(pt)

        left_c_raw = self.nose.get("leftContour", [])
        left_c: List[Point] = []
        for p in left_c_raw:
            pt = self.base.transform_point(base_point_xy(p))
            if pt is not None:
                left_c.append(pt)

        right_c_raw = self.nose.get("rightContour", [])
        right_c: List[Point] = []
        for p in right_c_raw:
            pt = self.base.transform_point(base_point_xy(p))
            if pt is not None:
                right_c.append(pt)

        nose_w = float(self.nose.get("width", 65.0)) * scale
        tip_r = max(nose_w * 0.22, 5.0)

        # 1. Glabella Keystone Root Transition
        keystone_raw = self.loomis.get("nosePlane", {}).get("keystone", [])
        if len(keystone_raw) >= 4:
            ks_pts = [self.base.transform_point(base_point_xy(p)) for p in keystone_raw]
            ks_pts = [p for p in ks_pts if p is not None]
            if len(ks_pts) >= 4:
                engine.quality.ghost_stroke(ks_pts + [ks_pts[0]], strength=0.25, width=0.68)

        # 2. Central dorsal nasal ridge (spine)
        if len(bridge_pts) >= 2:
            engine.quality.structural_stroke(bridge_pts, strength=0.78, width=1.10)

            # 3. Lateral side planes of the nasal bridge (delicate parallel guides)
            bridge_l: List[Point] = []
            bridge_r: List[Point] = []
            bw_half = nose_w * 0.16
            cos_a = math.cos(math.radians(alpha))
            sin_a = math.sin(math.radians(alpha))

            for p in bridge_pts[:5]:
                bridge_l.append((p[0] - bw_half * cos_a, p[1] - bw_half * sin_a))
                bridge_r.append((p[0] + bw_half * cos_a, p[1] + bw_half * sin_a))

            engine.quality.ghost_stroke(bridge_l, strength=0.26, width=0.65)
            engine.quality.ghost_stroke(bridge_r, strength=0.26, width=0.65)

        # 4. Ball of the nose (spherical tip construction)
        ball_pts = rotate_ellipse(tip_pt, tip_r, tip_r * 0.92, alpha, samples=36)
        engine.quality.construction_stroke(ball_pts, strength=0.42, width=0.82, closed=True)

        # 5. Alar wings (nostril flares)
        if len(left_c) >= 2:
            engine.quality.structural_stroke(left_c, strength=0.76, width=1.08)
        if len(right_c) >= 2:
            engine.quality.structural_stroke(right_c, strength=0.76, width=1.08)

        # 6. Under-plane trapezoid of the nose
        under_plane_raw = self.loomis.get("nosePlane", {}).get("underPlane", [])
        if len(under_plane_raw) >= 3:
            up_pts = [self.base.transform_point(base_point_xy(p)) for p in under_plane_raw]
            up_pts = [p for p in up_pts if p is not None]
            if len(up_pts) >= 3:
                engine.quality.ghost_stroke(up_pts + [up_pts[0]], strength=0.30, width=0.70)
        elif len(lower_pts) >= 2:
            engine.quality.structural_stroke(lower_pts, strength=0.68, width=0.92)

        # 6. Nostril openings (clean dark graphite accents)
        if len(left_c) >= 3:
            nostril_l_c = left_c[1]
            nostril_l = rotate_ellipse(
                nostril_l_c,
                tip_r * 0.42,
                tip_r * 0.22,
                alpha + 20.0,
                samples=20,
            )
            engine.quality.structural_stroke(nostril_l, strength=0.85, width=1.1, closed=True)

        if len(right_c) >= 3:
            nostril_r_c = right_c[1]
            nostril_r = rotate_ellipse(
                nostril_r_c,
                tip_r * 0.42,
                tip_r * 0.22,
                alpha - 20.0,
                samples=20,
            )
            engine.quality.structural_stroke(nostril_r, strength=0.85, width=1.1, closed=True)

    def render(self) -> Image.Image:
        """
        Render Stage 11 portrait construction page.
        Builds progressively on Stage 10 eyebrows, Stage 9 eyes, and Loomis base.
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
        self.base.draw_mouth(engine)
        self.base.draw_eyes(engine)
        self.base.draw_eyebrows(engine)

        # 5. Draw clean Stage 9 eyes
        alpha = float(self.eye_plane.get("angle", 0.0))
        nx = math.sin(math.radians(alpha))
        ny = -math.cos(math.radians(alpha))

        for side in ("right", "left"):
            edata = self.stage10.stage9.get_eye_side_data(side)
            if edata is not None:
                self.stage10.stage9.draw_clean_eye(engine, edata, nx, ny, alpha)

        # 6. Draw Stage 10 eyebrows and glabella
        r_brow = self.stage10.get_brow_points("right")
        l_brow = self.stage10.get_brow_points("left")

        if r_brow and l_brow:
            self.stage10.draw_glabella_keystone(engine, r_brow, l_brow)

        if r_brow:
            self.stage10.draw_eyebrow_mass(engine, r_brow, "right")

        if l_brow:
            self.stage10.draw_eyebrow_mass(engine, l_brow, "left")

        # 7. Draw Stage 11 Nose Refinement
        self.draw_nose_construction(engine, alpha)

        # 8. Apply graphite surface treatment and smoothing once
        final_image = engine.finalize()
        final_image = final_image.filter(
            ImageFilter.GaussianBlur(radius=0.10)
        )

        return final_image

    def save(self, output_path: Optional[Path] = None) -> Path:
        """Render and save Stage 11 PNG image."""
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
Stage11NoseConstruction = Stage11NoseRenderer


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
        description="Loomis AI - Stage 11 Nose Refinement"
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
    print("LOOMIS AI / STAGE 11 / NOSE REFINEMENT")
    print("=" * 62)
    print(f"Construction: {construction_path}")
    print(f"Output:       {output_path}\n")

    construction = load_construction(construction_path)
    renderer = Stage11NoseRenderer(construction)

    saved_path = renderer.save(output_path)

    print("=" * 62)
    print("SUCCESS")
    print("=" * 62)
    print(f"\nStage 11 created:\n{saved_path.resolve()}\n")
    print("Added:")
    print("  [OK] Loomis foundation, clean eyes, and eyebrows preserved")
    print("  [OK] Nasal dorsal bridge spine and lateral planes")
    print("  [OK] Spherical ball of the nose placement")
    print("  [OK] Alar wings and nostril flares")
    print("  [OK] Under-plane and dark graphite nostril openings")
    print("=" * 62)


if __name__ == "__main__":
    main()
