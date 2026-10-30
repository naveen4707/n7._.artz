"""
LOOMIS AI — MASTER GRAPHITE PORTRAIT RENDERER
STAGE 20: FINAL MASTER GRAPHITE PORTRAIT

Deterministic, landmark-accurate and photorealistic graphite portrait renderer.
Harmonizes:
  • Soft continuous graphite tonal modeling derived from the Black & White portrait picture
  • Subtle, authentic Andrew Loomis 3D structural underdrawing (Stages 1–7 scaffolding)
  • Anatomical face oval, jawline, and chin curvature
  • Natural hairline and authentic forehead marks / bindi
  • Beautiful arched eyebrows with layered hair flow
  • Clean almond eyes with kohl rim, iris fibers, solid 6B pupil, and pure-white specular catchlights
  • Sculpted nose with alar flares, crescent nostril accents, and subtle bridge contour
  • Full lips with Cupid's bow, sinuous closure line, lower lip cushion contour and highlight
  • Anatomical ears with 3D perspective occlusion for 3/4 views
  • Volumetric hair silhouette, crown volume, and framing curls
  • Slender cylindrical neck and elegant shoulder / garment contours
  • Cold-pressed art paper tooth and genuine graphite grain
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from bw_converter import get_bw_reference_path
from graphite_quality import GraphiteQualityEngine, GraphiteStyle
from hand_drawn_renderer import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    PAPER,
    TITLE,
    SUBTITLE,
)
from landmark_portrait_engine import LandmarkPortraitEngine, _catmull_rom_chain, _circle_pts

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = AI_ENGINE_DIR / "output"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"
ANALYSIS_FILE = OUTPUT_DIR / "analysis.json"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_20.png"

STAGE_NUMBER = 20
STAGE_NAME = "Final Graphite Portrait"

Point = Tuple[float, float]


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class Stage20FinalPortraitRenderer:
    """
    Stage 20: Final Master Graphite Portrait.
    Harmonizes full likeness contours, delicate features, hair volume, jewelry,
    drapery, continuous tonal graphite shading, and authentic Loomis underdrawing.
    """

    def __init__(
        self,
        construction: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None,
        img_path: Optional[Path] = None,
    ):
        self.construction = construction
        if analysis is None:
            analysis_p = ANALYSIS_FILE
            if analysis_p.exists():
                analysis = load_json(analysis_p)
            else:
                analysis = {}
        self.analysis = analysis
        self.img_path = Path(img_path) if img_path else (AI_ENGINE_DIR / "input" / "reference.jpg")
        self.lpe = LandmarkPortraitEngine(construction, analysis, img_path=self.img_path)
        self.scale = self.lpe.scale

    def _render_graphite_tone_base(self) -> Image.Image:
        """
        Extracts continuous tonal values from the Black & White portrait picture,
        warps them to exact canvas alignment, and blends them into soft graphite pencil washes.
        """
        # Ensure black and white reference exists
        bw_path = get_bw_reference_path(self.img_path)
        bw_img = cv2.imread(str(bw_path), cv2.IMREAD_GRAYSCALE)
        if bw_img is None:
            # Fallback to default canvas if B&W read fails
            return Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), PAPER)

        tf = self.lpe.base.transform
        scale = tf["scale"]
        offset_x = tf["offset_x"]
        offset_y = tf["offset_y"]

        # Affine matrix mapping source pixels to 1000x1200 canvas pixels
        M = np.array([
            [scale, 0, offset_x],
            [0, scale, offset_y]
        ], dtype=np.float32)

        warped_bw = cv2.warpAffine(bw_img, M, (CANVAS_WIDTH, CANVAS_HEIGHT), borderValue=255)

        # Build subject mask from facial landmarks + hair/neck volume
        landmarks = self.analysis.get("landmarks", [])
        subject_mask = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH), dtype=np.uint8)

        if landmarks:
            pts = np.array([
                [int(p["x"] * scale + offset_x), int(p["y"] * scale + offset_y)]
                for p in landmarks if 0 <= p["x"] * scale + offset_x < CANVAS_WIDTH and 0 <= p["y"] * scale + offset_y < CANVAS_HEIGHT
            ], dtype=np.int32)

            if len(pts) >= 6:
                hull = cv2.convexHull(pts)
                cv2.fillPoly(subject_mask, [hull], 255)

                # Generous dilation to enclose full volumetric hair crown, curls, ears, and shoulders
                dilate_px = int(max(200, scale * 300))
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_px, dilate_px))
                subject_mask = cv2.dilate(subject_mask, kernel)

                # Bottom extension for garment drapery down to canvas bottom
                max_lm_y = int(max(p[1] for p in pts))
                subject_mask[max_lm_y:, :] = 255

                # Smooth mask perimeter to feather naturally into paper tooth
                subject_mask = cv2.GaussianBlur(subject_mask, (85, 85), 0)
        else:
            subject_mask.fill(255)

        # Map pixel lightness to realistic graphite darkness:
        # Paper = (246, 245, 242), Dark Graphite = (28, 26, 24)
        norm_bw = warped_bw.astype(np.float32) / 255.0
        darkness = 1.0 - norm_bw

        # Studio-grade tonal curve: preserves luminous paper highlights,
        # provides delicate midtone modeling, and renders deep 6B graphite in hair & deep shadows
        darkness_curve = np.power(np.clip(darkness, 0.0, 1.0), 1.15) * 0.90
        mask_weight = (subject_mask.astype(np.float32) / 255.0)
        darkness = darkness_curve * mask_weight

        r_chan = np.clip(246.0 - darkness * (246.0 - 28.0), 0, 255).astype(np.uint8)
        g_chan = np.clip(245.0 - darkness * (245.0 - 26.0), 0, 255).astype(np.uint8)
        b_chan = np.clip(242.0 - darkness * (242.0 - 24.0), 0, 255).astype(np.uint8)
        tone_rgb = np.stack([r_chan, g_chan, b_chan], axis=-1)

        # Tortillon stump soft-focus blending for smooth skin planes
        tone_rgb = cv2.GaussianBlur(tone_rgb, (3, 3), 0)
        return Image.fromarray(tone_rgb, "RGB")

    def render(self) -> Image.Image:
        # 1. Base canvas with continuous tonal graphite modeling from B&W photo
        canvas = self._render_graphite_tone_base()
        draw = ImageDraw.Draw(canvas)

        # 2. Natural cold-pressed art paper grain & tooth
        rng = random.Random(2024)
        for _ in range(40000):
            gx = rng.randint(0, CANVAS_WIDTH - 1)
            gy = rng.randint(0, CANVAS_HEIGHT - 1)
            gv = rng.randint(236, 252)
            draw.point((gx, gy), fill=(gv, gv, gv))

        quality = GraphiteQualityEngine(
            canvas,
            seed=2024,
            style=GraphiteStyle(width=1.0, wobble=0.25, passes=3, grain_strength=3),
        )
        stroke_engine = type("EngineAdapter", (), {"quality": quality, "draw": draw})()

        # ─────────────────────────────────────────────────────────
        # 3. AUTHENTIC LOOMIS UNDERDRAWING (Whispering structural scaffolding)
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_loomis_underdrawing(stroke_engine, strength_factor=0.18)

        # ─────────────────────────────────────────────────────────
        # 4. PHOTO-ACCURATE SILHOUETTES & CONTOURS
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_hair_mass_contours(stroke_engine)
        self.lpe.draw_neck_and_garment(stroke_engine)

        # ─────────────────────────────────────────────────────────
        # 5. LANDMARK-DRIVEN ANATOMICAL REFINEMENT
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_face_oval(stroke_engine, strength=0.96, width=1.55)
        self.lpe.draw_hairline(stroke_engine, strength=0.68, width=1.05)
        self.lpe.draw_bindi(stroke_engine)

        # Clean almond eyes with limbal ring, pupil, and white specular catchlights
        self.lpe.draw_eye(stroke_engine, "left", iris_strength=0.96)
        self.lpe.draw_eye(stroke_engine, "right", iris_strength=0.96)

        # Arched eyebrows with natural hair flow
        self.lpe.draw_eyebrow(stroke_engine, "left")
        self.lpe.draw_eyebrow(stroke_engine, "right")

        # Sculpted nose with alar wings, crescent nostril accents, and bridge contour
        self.lpe.draw_nose(stroke_engine)

        # Full lips with Cupid's bow, sinuous line of closure, and corner nodes
        self.lpe.draw_lips(stroke_engine)

        # Anatomical ears (respecting 3/4 perspective occlusion)
        self.lpe.draw_ears_and_earrings(stroke_engine, strength=0.92)

        # ─────────────────────────────────────────────────────────
        # 6. TONAL GRAPHITE SHADOWS (Real lighting-driven value planes)
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_shadow_structures(stroke_engine)

        # ─────────────────────────────────────────────────────────
        # 7. SECONDARY DETAILS & FINE ACCENTS
        # ─────────────────────────────────────────────────────────
        # Delicate eyelash accents
        for side in ["left", "right"]:
            edata = self.lpe.get_eye_data(side)
            if edata and edata.get("outer"):
                p_out = edata["outer"]
                sign = -1 if side == "left" else 1
                for f_i in range(3):
                    f_ang = math.radians(-15 + f_i * 12)
                    f_len = (7.0 + f_i * 2.0) * self.scale
                    f_end = (p_out[0] + sign * f_len * math.cos(f_ang), p_out[1] - f_len * math.sin(f_ang))
                    quality.pencil_stroke([p_out, f_end], strength=0.88, width=0.90, passes=1)

        # ─────────────────────────────────────────────────────────
        # 8. CLASSICAL ATELIER HEADER & FOOTER
        # ─────────────────────────────────────────────────────────
        quality.draw.text((40, 30), f"LOOMIS AI | STAGE {STAGE_NUMBER:02d}", fill=TITLE)
        quality.draw.text((40, 62), STAGE_NAME.upper(), fill=TITLE)
        quality.draw.line((40, 105, 960, 105), fill=(205, 205, 201), width=1)
        quality.draw.text((40, 1140), "AI-generated graphite portrait — Full anatomical construction & CV analysis", fill=SUBTITLE)

        return quality.finalize()

    def save(self, output_path: Optional[Path] = None) -> Path:
        if output_path is None:
            output_path = DEFAULT_OUTPUT
        output_path = Path(output_path)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = self.render()
        img.save(str(output_path), quality=95)
        return output_path


def main():
    parser = argparse.ArgumentParser(description=f"Loomis AI - Stage {STAGE_NUMBER} {STAGE_NAME}")
    parser.add_argument("--input", default=str(CONSTRUCTION_FILE), help="Path to construction.json")
    parser.add_argument("--analysis", default=str(ANALYSIS_FILE), help="Path to analysis.json")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output image path")
    args = parser.parse_args()

    c_path = Path(args.input)
    a_path = Path(args.analysis)
    o_path = Path(args.output)

    if not c_path.exists():
        print(f"Error: {c_path} not found.")
        return

    construction = load_json(c_path)
    analysis = load_json(a_path) if a_path.exists() else None

    renderer = Stage20FinalPortraitRenderer(construction, analysis)
    saved = renderer.save(o_path)
    print(f"Stage {STAGE_NUMBER} rendered successfully: {saved}")


if __name__ == "__main__":
    main()
