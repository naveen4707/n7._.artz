"""CLI for M2.4 generative enhancement of a rendered Loomis stage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .model_adapter import OpenAIImageAdapter, GenerativeEnhancementError
    from .prompt_builder import build_enhancement_prompt
except ImportError:
    from model_adapter import OpenAIImageAdapter, GenerativeEnhancementError
    from prompt_builder import build_enhancement_prompt


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Loomis AI M2.4 generative graphite enhancement"
    )
    parser.add_argument("--stage", type=int, choices=range(1, 8), required=True)
    parser.add_argument(
        "--input",
        default=None,
        help="Input stage image. Defaults to output/hand_drawn/stage_XX.png",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path. Defaults to output/generative/stage_XX.png",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Image model override. Defaults to LOOMIS_IMAGE_MODEL or gpt-image-2.",
    )
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Print the exact enhancement prompt and exit.",
    )

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    default_input = (
        project_root
        / "output"
        / "hand_drawn"
        / f"stage_{args.stage:02d}.png"
    )
    default_output = (
        project_root
        / "output"
        / "generative"
        / f"stage_{args.stage:02d}.png"
    )

    input_path = Path(args.input) if args.input else default_input
    output_path = Path(args.output) if args.output else default_output

    prompt = build_enhancement_prompt(args.stage)

    if args.print_prompt:
        print(prompt)
        return 0

    print("=" * 64)
    print("LOOMIS AI / MEMBER 2 / M2.4")
    print("GENERATIVE GRAPHITE ENHANCEMENT")
    print("=" * 64)
    print(f"Stage : {args.stage}")
    print(f"Input : {input_path}")
    print(f"Output: {output_path}")

    try:
        adapter = OpenAIImageAdapter(model=args.model)
        result = adapter.enhance(
            image_path=input_path,
            output_path=output_path,
            prompt=prompt,
        )
    except GenerativeEnhancementError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Generated: {result}")
    print("M2.4 GENERATION: SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
