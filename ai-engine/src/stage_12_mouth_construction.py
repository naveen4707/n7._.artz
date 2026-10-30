"""
LOOMIS AI — MEMBER 2: GRAPHITE RENDERER
STAGE 12: MOUTH AND LIP REFINEMENT

Deterministic graphite construction renderer.
Constructs the mouth planes, lips, and oral architecture:
  - Preserves subtle Loomis cranium & jaw guide
  - Preserves clean eye construction (Stage 9)
  - Preserves eyebrow arches (Stage 10)
  - Preserves nose refinement (Stage 11)
  - Primary line of closure (interlabial aperture)
  - Corner commissure modiolus nodes
  - Upper lip vermilion contour and Cupid's bow
  - Lower lip vermilion curve
  - Philtrum columns connecting subnasale to Cupid's bow
  - Labiomental groove guide above the chin

Clean, anatomical linework without awkward wireframes or excessive hatching.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter

from graphite_quality import GraphiteQualityEngine, GraphiteStyle
from hand_drawn_renderer import (
    HandDrawnLoomisRenderer,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    PAPER,
    GRAPHITE_DARK,
    GRAPHITE,
    GRAPHITE_LIGHT,
    GRAPHITE_FAINT,
    TITLE,
    SUBTITLE,
)
from landmark_portrait_engine import LandmarkPortraitEngine, _catmull_rom_chain, _circle_pts

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = AI_ENGINE_DIR / "output"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"
ANALYSIS_FILE = OUTPUT_DIR / "analysis.json"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_12.png"

STAGE_NUMBER = 12
STAGE_NAME = "Mouth and Lip Refinement"

Point = Tuple[float, float]


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class Stage12MouthRenderer:
    """
    Stage 12: Mouth and Lip Refinement.
    Constructs the anatomical mouth and lips on top of the established face.
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
        # 1. Create fresh canvas with paper tone and grain
        canvas = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), PAPER)
        draw = ImageDraw.Draw(canvas)

        rng = random.Random(120)
        for _ in range(35000):
            gx = rng.randint(0, CANVAS_WIDTH - 1)
            gy = rng.randint(0, CANVAS_HEIGHT - 1)
            gv = rng.randint(237, 252)
            draw.point((gx, gy), fill=(gv, gv, gv))

        quality = GraphiteQualityEngine(
            canvas,
            seed=112,
            style=GraphiteStyle(width=1.0, wobble=0.30, passes=3, grain_strength=3),
        )
        stroke_engine = type("EngineAdapter", (), {"quality": quality, "draw": draw})()

        # 2. Subtle 2H Loomis Foundation (Faint guidelines)
        self.lpe.draw_loomis_underdrawing(stroke_engine, strength_factor=0.6)

        # 3. Jawline and Face Oval
        self.lpe.draw_face_oval(stroke_engine, strength=0.88, width=1.35)

        # 4. Clean Eyes (Stage 9)
        self.lpe.draw_eye(stroke_engine, "left")
        self.lpe.draw_eye(stroke_engine, "right")

        # 5. Arched Eyebrows (Stage 10)
        self.lpe.draw_eyebrow(stroke_engine, "left")
        self.lpe.draw_eyebrow(stroke_engine, "right")

        # 6. Sculpted Nose (Stage 11)
        self.lpe.draw_nose(stroke_engine)

        # 7. Focus: Refined Mouth and Lip Architecture (Stage 12)
        # Sinuous line of closure, Cupid's bow, lower lip curve, corner nodes
        self.lpe.draw_lips(stroke_engine)

        # Philtrum guide lines connecting subnasale to Cupid's bow peaks
        nose_data = self.lpe.get_nose_data()
        tip = nose_data["tip"]
        lip_data = self.lpe.get_lip_data()
        uo = lip_data.get("upper_outer")
        if tip and uo and len(uo) >= 6:
            p_center = uo[len(uo) // 2]
            quality.ghost_stroke(
                [(tip[0] - 4 * self.scale, tip[1] + 6 * self.scale),
                 (p_center[0] - 3 * self.scale, p_center[1] - 3 * self.scale)],
                strength=0.38, width=0.65
            )
            quality.ghost_stroke(
                [(tip[0] + 4 * self.scale, tip[1] + 6 * self.scale),
                 (p_center[0] + 3 * self.scale, p_center[1] - 3 * self.scale)],
                strength=0.38, width=0.65
            )

        # Labiomental groove guide (soft shadow line below bottom lip)
        lo = lip_data.get("lower_outer")
        chin = self.lpe.get_chin()
        if lo and chin and len(lo) >= 4:
            lo_mid = lo[len(lo) // 2]
            groove_y = lo_mid[1] + 8 * self.scale
            quality.ghost_stroke(
                [(lo_mid[0] - 12 * self.scale, groove_y),
                 (lo_mid[0], groove_y + 2 * self.scale),
                 (lo_mid[0] + 12 * self.scale, groove_y)],
                strength=0.45, width=0.75
            )

        # 8. Standard Stage Header & Footer
        quality.draw.text((40, 30), f"LOOMIS AI | STAGE {STAGE_NUMBER:02d}", fill=TITLE)
        quality.draw.text((40, 62), STAGE_NAME.upper(), fill=TITLE)
        quality.draw.line((40, 105, 960, 105), fill=(205, 205, 201), width=1)
        quality.draw.text((40, 1140), "AI-generated graphite construction — Anatomical oral architecture & Cupid's bow", fill=SUBTITLE)

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

    renderer = Stage12MouthRenderer(construction, analysis)
    saved = renderer.save(o_path)
    print(f"Stage {STAGE_NUMBER} rendered successfully: {saved}")


if __name__ == "__main__":
    main()
