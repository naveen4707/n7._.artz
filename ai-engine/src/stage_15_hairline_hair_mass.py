"""
LOOMIS AI — MEMBER 2: GRAPHITE RENDERER
STAGE 15: HAIRLINE AND HAIR MASS

Deterministic graphite construction renderer.
Constructs the hair volume, anatomical hairline boundary, and directional rhythm:
  - Subtle Loomis cranium & central axis underdrawing (Stages 1–7)
  - Clean eye construction (Stage 9)
  - Eyebrow arches (Stage 10)
  - Sculpted nose refinement (Stage 11)
  - Refined mouth and lip architecture (Stage 12)
  - Cheek and forehead planar contours (Stage 13)
  - Ear construction and earrings (Stage 14)
  - Hairline boundary curve across the forehead
  - Volumetric crown hair bun updo
  - Signature corkscrew ringlet curls framing temples and cheeks
"""

from __future__ import annotations

import argparse
import json
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
from landmark_portrait_engine import LandmarkPortraitEngine

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = AI_ENGINE_DIR / "output"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"
ANALYSIS_FILE = OUTPUT_DIR / "analysis.json"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_15.png"

STAGE_NUMBER = 15
STAGE_NAME = "Hairline and Hair Mass"

Point = Tuple[float, float]


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class Stage15HairlineHairMassRenderer:
    """
    Stage 15: Hairline and Hair Mass.
    Constructs the volumetric crown hair bun updo, hairline, and signature curls.
    """

    def __init__(
        self,
        construction: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None,
        img_path: Optional[Any] = None,
    ):
        self.construction = construction
        if analysis is None:
            analysis_p = ANALYSIS_FILE
            if analysis_p.exists():
                analysis = load_json(analysis_p)
            else:
                analysis = {}
        self.analysis = analysis
        self.img_path = img_path
        self.lpe = LandmarkPortraitEngine(construction, analysis, img_path=img_path)
        self.scale = self.lpe.scale

    def render(self) -> Image.Image:
        canvas = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), PAPER)
        draw = ImageDraw.Draw(canvas)

        rng = random.Random(150)
        for _ in range(35000):
            gx = rng.randint(0, CANVAS_WIDTH - 1)
            gy = rng.randint(0, CANVAS_HEIGHT - 1)
            gv = rng.randint(237, 252)
            draw.point((gx, gy), fill=(gv, gv, gv))

        quality = GraphiteQualityEngine(
            canvas,
            seed=115,
            style=GraphiteStyle(width=1.0, wobble=0.30, passes=3, grain_strength=3),
        )
        stroke_engine = type("EngineAdapter", (), {"quality": quality, "draw": draw})()

        # 1. Subtle 2H Loomis Foundation (Faint guidelines)
        self.lpe.draw_loomis_underdrawing(stroke_engine, strength_factor=0.45)

        # 2. Jawline and Face Oval
        self.lpe.draw_face_oval(stroke_engine, strength=0.88, width=1.35)

        # 3. Clean Eyes (Stage 9)
        self.lpe.draw_eye(stroke_engine, "left")
        self.lpe.draw_eye(stroke_engine, "right")

        # 4. Arched Eyebrows (Stage 10)
        self.lpe.draw_eyebrow(stroke_engine, "left")
        self.lpe.draw_eyebrow(stroke_engine, "right")

        # 5. Sculpted Nose (Stage 11)
        self.lpe.draw_nose(stroke_engine)

        # 6. Refined Mouth & Lips (Stage 12)
        self.lpe.draw_lips(stroke_engine)

        # 7. Cheek, Forehead & Chin Contours (Stage 13)
        self.lpe.draw_cheek_forehead_contours(stroke_engine, strength=0.40)

        # 8. Ear Construction & Earrings (Stage 14)
        self.lpe.draw_ears_and_earrings(stroke_engine, strength=0.88)

        # 9. Focus: Hairline & Volumetric Hair Bun with Ringlets (Stage 15)
        self.lpe.draw_hairline(stroke_engine, strength=0.70, width=1.05)
        self.lpe.draw_hair_bun_and_ringlets(stroke_engine, rng=random.Random(1515))

        # 10. Standard Stage Header & Footer
        quality.draw.text((40, 30), f"LOOMIS AI | STAGE {STAGE_NUMBER:02d}", fill=TITLE)
        quality.draw.text((40, 62), STAGE_NAME.upper(), fill=TITLE)
        quality.draw.line((40, 105, 960, 105), fill=(205, 205, 201), width=1)
        quality.draw.text((40, 1140), "AI-generated graphite construction — Volumetric hair bun updo & tumbling ringlets", fill=SUBTITLE)

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

    renderer = Stage15HairlineHairMassRenderer(construction, analysis)
    saved = renderer.save(o_path)
    print(f"Stage {STAGE_NUMBER} rendered successfully: {saved}")


if __name__ == "__main__":
    main()
