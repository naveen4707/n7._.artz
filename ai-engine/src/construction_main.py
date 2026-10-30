import argparse
import json
import sys
from pathlib import Path

from loomis_geometry import LoomisGeometry


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Loomis AI - Construction Geometry"
    )

    parser.add_argument(
        "--input",
        default="output/analysis.json",
        help="Path to analysis JSON"
    )

    parser.add_argument(
        "--output",
        default="output/construction.json",
        help="Path to construction JSON"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_absolute():
        input_path = Path.cwd() / input_path

    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    print("=" * 55)
    print("              LOOMIS AI")
    print("       MEMBER 2 - CONSTRUCTION")
    print("=" * 55)

    print()
    print(f"Analysis: {input_path}")

    if not input_path.exists():
        print()
        print("ERROR: Analysis file not found.")
        print(input_path)
        sys.exit(1)

    # -----------------------------------------------------
    # Load Member 1 result
    # -----------------------------------------------------

    print()
    print("Loading visual analysis...")

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as file:
        analysis = json.load(file)

    if not analysis.get("success"):
        print()
        print("ERROR: Member 1 analysis was not successful.")
        sys.exit(1)

    print("Visual analysis loaded.")

    # -----------------------------------------------------
    # Generate Loomis construction
    # -----------------------------------------------------

    print()
    print("Building Loomis construction geometry...")

    geometry = LoomisGeometry(
        analysis
    )

    construction = geometry.build()

    print("Construction geometry generated.")

    # -----------------------------------------------------
    # Save result
    # -----------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            construction,
            file,
            indent=2,
            ensure_ascii=False
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print()
    print("=" * 55)
    print("          CONSTRUCTION SUMMARY")
    print("=" * 55)

    print()
    print(
        f"Pose Type:       "
        f"{construction['source']['poseType']}"
    )

    print(
        f"Direction:       "
        f"{construction['source']['direction']}"
    )

    print()
    print("Stages generated:")

    for stage_name in construction["stages"]:
        print(f"  ✓ {stage_name}")

    print()
    print("Construction saved:")
    print(output_path.resolve())

    print()
    print("=" * 55)


if __name__ == "__main__":
    main()