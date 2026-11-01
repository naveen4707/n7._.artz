"""
LOOMIS AI — MASTER GRAPHITE PORTRAIT RENDERER
STAGE 20: FINAL MASTER GRAPHITE PORTRAIT

Deterministic, landmark-accurate, and 100% hand-drawn graphite portrait renderer.
Pure procedural graphite rendering without photo-overlay or raster blending:
  • Cold-pressed art paper tooth and genuine graphite grain
  • Whispering Andrew Loomis 3D structural underdrawing (Stages 1–7 scaffolding)
  • Anatomical face oval, jawline, and rounded chin curvature
  • Natural hairline and authentic forehead marks / bindi
  • Beautiful arched eyebrows with layered 3-part hair flow
  • Almond eyes with kohl rim, iris fibers, solid 6B pupil, and pure-white specular catchlights
  • Sculpted 5-plane nose with alar flares, crescent nostril accents, and bridge contour
  • Full lips with Cupid's bow, sinuous closure line, lower lip cushions, and luminous highlight
  • Anatomical ears with 3D perspective occlusion for 3/4 views
  • Volumetric hair mass, crown volume, and directional hair flow graphite tone
  • Slender cylindrical neck and elegant shoulder / garment contours
  • Hand-drawn graphite value cross-hatching across anatomical planes
  • Soft eraser-lift luminous highlights on pupils, nose ball, and lower lip
  • Elegant cursive atelier artist signature and seal
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image, ImageDraw

from graphite_quality import GraphiteQualityEngine, GraphiteStyle
from hand_drawn_renderer import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    PAPER,
    TITLE,
    SUBTITLE,
)
from landmark_portrait_engine import LandmarkPortraitEngine, _catmull_rom_chain

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
    Pure hand-drawn graphite portrait harmonizing full anatomical likeness contours,
    delicate features, volumetric hair shading, fabric drapery, classical Loomis underdrawing,
    and hand-drawn graphite tonal cross-hatching.
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

    def render(self) -> Image.Image:
        # 1. Base canvas: genuine cold-pressed art paper
        canvas = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), PAPER)
        draw = ImageDraw.Draw(canvas)

        # 2. Natural cold-pressed art paper grain & tooth
        rng = random.Random(2024)
        for _ in range(45000):
            gx = rng.randint(0, CANVAS_WIDTH - 1)
            gy = rng.randint(0, CANVAS_HEIGHT - 1)
            gv = rng.randint(236, 252)
            draw.point((gx, gy), fill=(gv, gv, gv))

        quality = GraphiteQualityEngine(
            canvas,
            seed=2024,
            style=GraphiteStyle(width=1.05, wobble=0.25, passes=3, grain_strength=3),
        )
        stroke_engine = type("EngineAdapter", (), {"quality": quality, "draw": draw})()

        # ─────────────────────────────────────────────────────────
        # 3. AUTHENTIC LOOMIS UNDERDRAWING (Whispering structural scaffolding)
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_loomis_underdrawing(stroke_engine, strength_factor=0.18)

        # ─────────────────────────────────────────────────────────
        # 4. PHOTO-ACCURATE SILHOUETTES, HAIR VOLUME & DRAPERY
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_hair_mass_contours(stroke_engine)
        self.lpe.draw_hair_tonal_volume(stroke_engine, rng=random.Random(2024))
        self.lpe.draw_neck_and_garment(stroke_engine, structural_only=False)

        # ─────────────────────────────────────────────────────────
        # 5. LANDMARK-DRIVEN ANATOMICAL REFINEMENT
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_face_oval(stroke_engine, strength=0.96, width=1.55)
        self.lpe.draw_hairline(stroke_engine, strength=0.68, width=1.05)
        self.lpe.draw_bindi(stroke_engine)
        self.lpe.draw_cheek_forehead_contours(stroke_engine, strength=0.22)

        # Clean almond eyes with limbal ring, pupil, and white specular catchlights
        self.lpe.draw_eye(stroke_engine, "left", iris_strength=0.96)
        self.lpe.draw_eye(stroke_engine, "right", iris_strength=0.96)

        # Arched eyebrows with natural 3-part hair flow
        self.lpe.draw_eyebrow(stroke_engine, "left")
        self.lpe.draw_eyebrow(stroke_engine, "right")

        # Sculpted 5-plane nose with alar wings, crescent nostril accents, and bridge contour
        self.lpe.draw_nose(stroke_engine)

        # Full lips with Cupid's bow, sinuous line of closure, and corner nodes
        self.lpe.draw_lips(stroke_engine)

        # Anatomical ears (respecting 3/4 perspective occlusion)
        self.lpe.draw_ears_and_earrings(stroke_engine, strength=0.92)

        # ─────────────────────────────────────────────────────────
        # 6. TONAL GRAPHITE SHADOWS (Real lighting-driven value planes)
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_shadow_structures(stroke_engine, rng=random.Random(2024))

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

        # Saree / garment fabric fold shading
        cloth_contours = self.lpe.extractor.get_clothing_contours()
        for pts in cloth_contours[::2]:
            if len(pts) >= 4:
                quality.ghost_stroke(_catmull_rom_chain(pts, 2), strength=0.45, width=0.75)

        # ─────────────────────────────────────────────────────────
        # 8. LUMINOUS HIGHLIGHTS & ERASER LIFTS
        # ─────────────────────────────────────────────────────────
        self.lpe.draw_luminous_highlights(quality.image)

        # ─────────────────────────────────────────────────────────
        # 9. ATELIER ARTIST SIGNATURE & FLOURISH
        # ─────────────────────────────────────────────────────────
        # Hand-drawn atelier signature in lower-right margin
        quality.draw.text((700, 1075), "Andrew Loomis Method", fill=(80, 77, 72))
        quality.draw.text((700, 1095), "LoomisAI Atelier", fill=(115, 112, 106))
        # Flowing cursive signature flourish underline in graphite
        quality.pencil_stroke(
            [(695, 1115), (755, 1113), (835, 1110), (910, 1116), (940, 1112)],
            strength=0.68,
            width=0.95,
            wobble=0.30,
            passes=2,
        )

        # ─────────────────────────────────────────────────────────
        # 10. CLASSICAL ATELIER HEADER & FOOTER
        # ─────────────────────────────────────────────────────────
        quality.draw.text((40, 30), f"LOOMIS AI | STAGE {STAGE_NUMBER:02d}", fill=TITLE)
        quality.draw.text((40, 62), STAGE_NAME.upper(), fill=TITLE)
        quality.draw.line((40, 105, 960, 105), fill=(205, 205, 201), width=1)
        quality.draw.text((40, 1140), "AI-generated graphite portrait — Master Andrew Loomis method & anatomical construction", fill=SUBTITLE)

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
