"""
LOOMIS AI — MEMBER 2: GRAPHITE RENDERER
STAGE 13: CHEEK AND FOREHEAD CONTOURS

Deterministic graphite construction renderer.
Constructs the major planar landmarks of the skull:
  - Subtle Loomis cranium & central axis underdrawing (Stages 1–7)
  - Clean eye construction (Stage 9)
  - Eyebrow arches (Stage 10)
  - Sculpted nose refinement (Stage 11)
  - Refined mouth and lip architecture (Stage 12)
  - Zygomatic cheekbone planes connecting brow tails to cheek apex and jaw
  - Temporal crest and forehead planes connecting brow to cranium top
  - Mental protuberance (chin ball) construction guide
  - Nasolabial fold guides connecting alar wings toward mouth corners

Clean, anatomical linework without awkward wireframes or excessive hatching.
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
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_13.png"

STAGE_NUMBER = 13
STAGE_NAME = "Cheek and Forehead Contours"

Point = Tuple[float, float]


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class Stage13CheekForeheadRenderer:
    """
    Stage 13: Cheek and Forehead Contours.
    Constructs the planar landmarks of the skull (zygomatic cheekbones, forehead, and chin ball).
    """

    def __init__(
        self,
        construction: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None,
    ):
        self.construction = construction
        if analysis is None:
            analysis_p = ANALYSIS_FILE
            if analysis_p.exists():
                analysis = load_json(analysis_p)
            else:
                analysis = {}
        self.analysis = analysis
        self.lpe = LandmarkPortraitEngine(construction, analysis)
        self.scale = self.lpe.scale

    def render(self) -> Image.Image:
        canvas = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), PAPER)
        draw = ImageDraw.Draw(canvas)

        rng = random.Random(130)
        for _ in range(35000):
            gx = rng.randint(0, CANVAS_WIDTH - 1)
            gy = rng.randint(0, CANVAS_HEIGHT - 1)
            gv = rng.randint(237, 252)
            draw.point((gx, gy), fill=(gv, gv, gv))

        quality = GraphiteQualityEngine(
            canvas,
            seed=113,
            style=GraphiteStyle(width=1.0, wobble=0.30, passes=3, grain_strength=3),
        )
        stroke_engine = type("EngineAdapter", (), {"quality": quality, "draw": draw})()

        # 1. Subtle 2H Loomis Foundation (Faint guidelines)
        self.lpe.draw_loomis_underdrawing(stroke_engine, strength_factor=0.55)

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

        # 7. Focus: Cheek, Forehead & Chin Contours (Stage 13)
        self.lpe.draw_cheek_forehead_contours(stroke_engine, strength=0.85)

        # 8. Standard Stage Header & Footer
        quality.draw.text((40, 30), f"LOOMIS AI | STAGE {STAGE_NUMBER:02d}", fill=TITLE)
        quality.draw.text((40, 62), STAGE_NAME.upper(), fill=TITLE)
        quality.draw.line((40, 105, 960, 105), fill=(205, 205, 201), width=1)
        quality.draw.text((40, 1140), "AI-generated graphite construction — Zygomatic cheek planes & mental protuberance", fill=SUBTITLE)

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

    renderer = Stage13CheekForeheadRenderer(construction, analysis)
    saved = renderer.save(o_path)
    print(f"Stage {STAGE_NUMBER} rendered successfully: {saved}")


if __name__ == "__main__":
    main()
