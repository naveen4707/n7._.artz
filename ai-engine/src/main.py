import argparse
import json
import sys
from pathlib import Path

from config import (
    DEFAULT_OUTPUT_FILE,
    FACE_LANDMARKER_MODEL,
    MIN_FACE_DETECTION_CONFIDENCE,
    MIN_FACE_PRESENCE_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    NUM_FACES,
    validate_project,
)

from landmark_analyzer import LandmarkAnalyzer
from pose_estimator import PoseEstimator
from face_analyzer import FaceAnalyzer


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Loomis AI - Member 1 Face Analysis"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the reference portrait."
    )

    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_FILE),
        help="Path for the analysis JSON."
    )

    return parser.parse_args()


def print_summary(result):
    print()
    print("=" * 50)
    print("          LOOMIS AI - ANALYSIS")
    print("=" * 50)

    if not result.get("success"):
        print()
        print("STATUS: FAILED")
        print()
        print(result.get("error", "Unknown error"))
        return

    image = result["image"]
    face = result["face"]
    pose = result["pose"]
    measurements = result["measurements"]

    print()
    print("IMAGE")
    print("-" * 50)
    print(f"Width:          {image['width']}")
    print(f"Height:         {image['height']}")

    print()
    print("FACE")
    print("-" * 50)
    print(f"Detected:       {face['detected']}")
    print(f"Landmarks:      {face['landmarkCount']}")

    print()
    print("HEAD POSE")
    print("-" * 50)
    print(f"Yaw:             {pose['yaw']}°")
    print(f"Pitch:           {pose['pitch']}°")
    print(f"Roll:            {pose['roll']}°")
    print(f"Orientation:     {pose['orientation']}")
    print(f"Direction:       {pose['direction']}")
    print(f"Pose Type:       {pose['poseType']}")
    print(f"Confidence:      {pose['confidence']}")

    print()
    print("MEASUREMENTS")
    print("-" * 50)
    print(f"Head Width:      {measurements['headWidth']}")
    print(f"Face Length:     {measurements['faceLength']}")
    print(f"Eye Distance:    {measurements['eyeDistance']}")
    print(f"Mouth Width:     {measurements['mouthWidth']}")
    print(f"Jaw Width:       {measurements['jawWidth']}")
    print(f"Face Ratio:      {measurements['faceAspectRatio']}")

    print()
    print("=" * 50)


def main():
    args = parse_arguments()

    validate_project()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_absolute():
        input_path = Path.cwd() / input_path

    if not input_path.exists():
        print(
            f"ERROR: Input image not found:\n"
            f"{input_path}"
        )
        sys.exit(1)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 50)
    print("             LOOMIS AI")
    print("       MEMBER 1 - VISUAL ANALYSIS")
    print("=" * 50)

    print()
    print(f"Input: {input_path}")
    print(f"Model: {FACE_LANDMARKER_MODEL}")

    print()
    print("Loading Face Landmarker...")

    landmark_analyzer = LandmarkAnalyzer(
        model_path=FACE_LANDMARKER_MODEL,
        num_faces=NUM_FACES,
        min_face_detection_confidence=(
            MIN_FACE_DETECTION_CONFIDENCE
        ),
        min_face_presence_confidence=(
            MIN_FACE_PRESENCE_CONFIDENCE
        ),
        min_tracking_confidence=(
            MIN_TRACKING_CONFIDENCE
        ),
    )

    print("Face Landmarker loaded.")

    pose_estimator = PoseEstimator()

    analyzer = FaceAnalyzer(
        landmark_analyzer=landmark_analyzer,
        pose_estimator=pose_estimator,
    )

    try:
        print()
        print("Analyzing reference image...")

        result = analyzer.analyze(
            input_path
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        print_summary(result)

        print()
        print("Analysis saved:")
        print(output_path.resolve())
        print()

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()