"""
LOOMIS AI — STAGE 20: ACCURATE FINAL GRAPHITE PORTRAIT
Alias / wrapper pointing to Stage20FinalPortraitRenderer for complete compatibility.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from stage_20_final_portrait import (
    Stage20FinalPortraitRenderer,
    CONSTRUCTION_FILE,
    ANALYSIS_FILE,
    DEFAULT_OUTPUT,
    STAGE_NUMBER,
    STAGE_NAME,
    load_json,
)

Stage20AccuratePortraitRenderer = Stage20FinalPortraitRenderer


def main():
    parser = argparse.ArgumentParser(description="Loomis AI - Stage 20 Final Accurate Portrait")
    parser.add_argument("--construction", default=str(CONSTRUCTION_FILE), help="Path to construction.json")
    parser.add_argument("--analysis", default=str(ANALYSIS_FILE), help="Path to analysis.json")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output image path")
    args = parser.parse_args()

    c_path = Path(args.construction)
    a_path = Path(args.analysis)
    o_path = Path(args.output)

    if not c_path.exists() or not a_path.exists():
        print("Error: Input files not found.")
        return

    construction = load_json(c_path)
    analysis = load_json(a_path)

    renderer = Stage20FinalPortraitRenderer(construction, analysis)
    saved = renderer.save(o_path)
    print(f"Stage 20 rendered successfully: {saved}")


if __name__ == "__main__":
    main()
