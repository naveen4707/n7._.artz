"""
LOOMIS AI — MEMBER 2: GRAPHITE RENDERER
STAGE 09: EYEBALL AND EYELID CONSTRUCTION (CLEAN GRAPHITE EDITION)

Deterministic graphite construction renderer.
Builds clean, elegant anatomical eye construction:
  - Faint underlying spherical eyeball placement
  - Confirmed upper eyelid contour wrapping over the eyeball
  - Subtle, clean supratarsal crease (eyelid fold)
  - Delicate lower eyelid rim
  - Anatomical medial canthus (tear-duct) at inner corner
  - Clean, focused iris and pupil with specular catchlight

Avoids awkward, cluttered concentric lines or wireframe noise.
Preserves the validated Loomis construction foundation (Stages 1–7).
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
from stage_08_eye_construction import (
    Stage8EyeConstruction,
    rotate_ellipse,
    eye_data,
)


# ============================================================
# PATHS AND STAGE CONFIGURATION
# ============================================================

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = AI_ENGINE_DIR / "output"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_09.png"

STAGE_NUMBER = 9
STAGE_NAME = "Eyeball and Eyelid Construction"

Point = Tuple[float, float]


# ============================================================
# STAGE 09 RENDERER
# ============================================================

class Stage09EyeRenderer:
    """
    Stage 09: Clean Eyeball and Eyelid Construction.

    Builds on top of the validated Loomis foundation (Stages 1–7)
    with clean, readable artist construction:
      - Subtle brow bone guide
      - Single faint eyeball construction ellipse
      - Confirmed structural upper eyelid
      - Delicate upper eyelid crease
      - Clean lower eyelid contour
      - Medial canthus tear-duct
      - Focused iris and dark pupil with catchlight
    """

    def __init__(self, construction: Dict[str, Any]):
        self.construction = construction
        self.base = HandDrawnLoomisRenderer(construction)

        self.face = construction.get("accurateFace", {})
        self.eyes = self.face.get("eyes", {})
        self.loomis = construction.get("loomis", {})
        self.eye_plane = self.loomis.get("eyePlane", {})

    def get_eye_side_data(self, side: str) -> Optional[Dict[str, Any]]:
        """Extract validated eye data transformed to canvas coordinates."""
        try:
            raw = eye_data(self.eyes, side)
        except (ValueError, KeyError):
            return None

        canvas_points: List[Point] = []
        for p in raw["points"]:
            transformed = self.base.transform_point(p)
            if transformed is not None:
                canvas_points.append(transformed)

        center = self.base.transform_point(raw["center"])
        if len(canvas_points) < 4 or center is None:
            return None

        scale = self.base.transform["scale"]
        width = raw["width"] * scale
        height = raw["height"] * scale

        if width <= 0 or height <= 0:
            return None

        return {
            "side": side,
            "center": center,
            "points": canvas_points,
            "width": width,
            "height": height,
            "indices": raw.get("indices", []),
        }

    def draw_clean_eye(
        self,
        engine: GraphiteStrokeEngine,
        data: Dict[str, Any],
        nx: float,
        ny: float,
        alpha: float,
    ) -> None:
        """
        Draw clean, uncluttered eye construction for one side.
        Avoids redundant concentric rings, heavy hatching, or wireframe noise.
        """
        center = data["center"]
        points = data["points"]
        indices = data["indices"]
        width = data["width"]
        height = data["height"]
        side = data["side"]

        eyeball_rx = max(width * 0.47, 3.5)
        eyeball_ry = max(height * 0.86, 3.5)
        iris_rx = max(min(width * 0.19, eyeball_rx * 0.42), 2.0)
        iris_ry = max(min(height * 0.38, eyeball_ry * 0.55), 2.0)

        # 1. Subtle brow bone socket guide (single faint upward arc)
        sup_c = (
            center[0] + nx * (height * 0.55),
            center[1] + ny * (height * 0.55),
        )
        sup_pts: List[Point] = []
        rot_rad = math.radians(alpha)
        for i in range(25):
            t = math.radians(200.0 + (340.0 - 200.0) * (i / 24.0))
            lx = (width * 0.55) * math.cos(t)
            ly = (height * 0.30) * math.sin(t)
            sup_pts.append((
                sup_c[0] + lx * math.cos(rot_rad) - ly * math.sin(rot_rad),
                sup_c[1] + lx * math.sin(rot_rad) + ly * math.cos(rot_rad),
            ))
        engine.quality.ghost_stroke(sup_pts, strength=0.14, width=0.60)

        # 2. Eyeball sphere - faint searching construction ellipse
        eyeball = rotate_ellipse(center, eyeball_rx, eyeball_ry, alpha, samples=64)
        engine.quality.ghost_stroke(eyeball, strength=0.20, width=0.65, closed=True)

        # 3. Clean eyelid contours
        inner_idx = 133 if side == "right" else 362
        if inner_idx in indices:
            split_idx = indices.index(inner_idx)
            path1 = points[:split_idx + 1]
            path2 = points[split_idx:] + [points[0]]
        else:
            mid = max(2, len(points) // 2)
            path1 = points[:mid]
            path2 = points[mid:]

        avg_y1 = sum(p[1] for p in path1) / len(path1)
        avg_y2 = sum(p[1] for p in path2) / len(path2)
        upper_lid = path2 if avg_y2 < avg_y1 else path1
        lower_lid = path1 if avg_y2 < avg_y1 else path2

        is_closed = (height / max(1.0, width)) < 0.18 or bool(self.construction.get("pose", {}).get("eyesClosed", False))

        # Confirmed upper eyelid - elegant, confident line
        if len(upper_lid) >= 2:
            engine.quality.structural_stroke(upper_lid, strength=0.88 if is_closed else 0.82, width=1.20 if is_closed else 1.15)

            # Single clean upper eyelid crease (natural supratarsal fold above the lid)
            crease_pts: List[Point] = []
            crease_h = (height * 0.35 + 2.5) if is_closed else (height * 0.20)
            n_up = len(upper_lid)
            for i, p in enumerate(upper_lid):
                t = i / max(1, n_up - 1)
                off = crease_h * math.sin(t * math.pi)
                crease_pts.append((p[0] + nx * off, p[1] + ny * off))
            engine.quality.construction_stroke(crease_pts, strength=0.40 if is_closed else 0.35, width=0.75 if is_closed else 0.72)

        # Lower eyelid - clean, delicate structural line
        if not is_closed and len(lower_lid) >= 2:
            engine.quality.structural_stroke(lower_lid, strength=0.55, width=0.90)

        # 4. Tear duct (medial canthus) - clean small anatomical inner corner
        if inner_idx in indices:
            inner_pt = points[indices.index(inner_idx)]
            nose_dir = 1.0 if side == "right" else -1.0
            duct_c = (inner_pt[0] + nose_dir * (width * 0.035), inner_pt[1])
            duct_rx = width * 0.055
            duct_ry = height * 0.14
            duct_pts = rotate_ellipse(duct_c, duct_rx, duct_ry, alpha, samples=24)
            engine.quality.construction_stroke(duct_pts, strength=0.40, width=0.75, closed=True)

        if is_closed:
            # Soft downward resting eyelash ticks for closed eyelids (no iris or pupil!)
            for i in range(1, len(upper_lid) - 1, 2):
                pt = upper_lid[i]
                lash_end = (pt[0] - nx * 2.8, pt[1] - ny * 2.8)
                engine.quality.ghost_stroke([pt, lash_end], strength=0.50, width=0.65)
            return

        # 5. Iris and pupil - clean, sharp, focused (Open eyes only)
        iris_pts = rotate_ellipse(center, iris_rx, iris_ry, alpha, samples=48)
        engine.quality.structural_stroke(iris_pts, strength=0.68, width=0.95, closed=True)

        pupil_r = max(min(iris_rx, iris_ry) * 0.32, 1.5)
        pupil_pts = rotate_ellipse(center, pupil_r, pupil_r, 0.0, samples=32)
        engine.quality.structural_stroke(pupil_pts, strength=0.88, width=1.15, closed=True)

        # Clean specular catchlight
        hl_c = (center[0] - pupil_r * 0.35, center[1] - pupil_r * 0.35)
        hl_r = max(pupil_r * 0.28, 0.8)
        hl_pts = rotate_ellipse(hl_c, hl_r, hl_r, 0.0, samples=16)
        engine.quality.ghost_stroke(hl_pts, strength=0.40, width=0.60, closed=True)

    def render(self) -> Image.Image:
        """
        Render Stage 09 portrait construction page cleanly.
        Preserves Stages 1–7 foundation and adds clean eye construction.
        """
        # 1. Create fresh canvas
        image = self.base.create_canvas()

        # 2. Create single stroke engine
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

        # 5. Draw clean Stage 9 eyeball and eyelid construction
        alpha = float(self.eye_plane.get("angle", 0.0))
        nx = math.sin(math.radians(alpha))
        ny = -math.cos(math.radians(alpha))

        for side in ("right", "left"):
            data = self.get_eye_side_data(side)
            if data is not None:
                self.draw_clean_eye(engine, data, nx, ny, alpha)

        # 6. Apply graphite surface treatment and smoothing once
        final_image = engine.finalize()
        final_image = final_image.filter(
            ImageFilter.GaussianBlur(radius=0.10)
        )

        return final_image

    def save(self, output_path: Optional[Path] = None) -> Path:
        """Render and save Stage 9 PNG image."""
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
Stage9EyeballEyelidConstruction = Stage09EyeRenderer


# ============================================================
# CLI AND HELPERS
# ============================================================

def load_construction(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate construction.json."""
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

    if not isinstance(construction, dict):
        raise ValueError("construction.json must contain a JSON object.")

    if "accurateFace" not in construction:
        raise KeyError("construction.json is missing 'accurateFace'.")

    if "loomis" not in construction:
        raise KeyError("construction.json is missing 'loomis'.")

    return construction


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Loomis AI - Stage 09 Eyeball and Eyelid Construction"
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
    print("LOOMIS AI / STAGE 9 / EYEBALL + EYELID CONSTRUCTION")
    print("=" * 62)
    print(f"Construction: {construction_path}")
    print(f"Output:       {output_path}\n")

    construction = load_construction(construction_path)
    renderer = Stage09EyeRenderer(construction)

    available = [
        side for side in ("right", "left")
        if renderer.get_eye_side_data(side) is not None
    ]
    if not available:
        raise RuntimeError("No usable eye geometry found in accurateFace.eyes.")

    saved_path = renderer.save(output_path)

    print("=" * 62)
    print("SUCCESS")
    print("=" * 62)
    print(f"\nStage 9 created:\n{saved_path.resolve()}\n")
    print("Added:")
    print("  [OK] Loomis foundation (Stages 1–7) preserved")
    print("  [OK] Clean, natural eyelid contours")
    print("  [OK] Subtle supratarsal fold (eyelid crease)")
    print("  [OK] Anatomical tear duct (medial canthus)")
    print("  [OK] Focused iris and dark graphite pupil with specular catchlight")
    print(f"\nEyes constructed: {len(available)} ({', '.join(available)})")
    print("=" * 62)


if __name__ == "__main__":
    main()
