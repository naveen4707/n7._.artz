import json
import math
from pathlib import Path


# =========================================================
# LOOMIS AI
# ALIGNMENT VALIDATOR v5.0
# =========================================================
#
# Purpose:
#
#   Validate the relationship between:
#
#       MediaPipe 478 landmarks
#               ↓
#       Loomis construction geometry
#
# This file is completely independent from the renderer.
#
# It DOES NOT modify construction geometry.
# It DOES NOT modify analysis data.
# It ONLY measures alignment.
#
# =========================================================


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYSIS_FILE = (
    BASE_DIR
    / "output"
    / "analysis.json"
)

CONSTRUCTION_FILE = (
    BASE_DIR
    / "output"
    / "construction.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "alignment_validation.json"
)


# ---------------------------------------------------------
# GEOMETRY HELPERS
# ---------------------------------------------------------

def distance(point_a, point_b):
    """
    Euclidean 2D distance between two points.
    """

    dx = (
        float(point_a["x"])
        -
        float(point_b["x"])
    )

    dy = (
        float(point_a["y"])
        -
        float(point_b["y"])
    )

    return math.sqrt(
        dx * dx +
        dy * dy
    )


def midpoint(point_a, point_b):
    """
    Calculate midpoint between two points.
    """

    return {
        "x": (
            float(point_a["x"])
            +
            float(point_b["x"])
        ) / 2.0,

        "y": (
            float(point_a["y"])
            +
            float(point_b["y"])
        ) / 2.0,
    }


def landmark_point(landmarks, index):
    """
    Return a simplified 2D point from a MediaPipe landmark.
    """

    landmark = landmarks[index]

    return {
        "x": float(landmark["x"]),
        "y": float(landmark["y"]),
    }


def average(values):
    """
    Safe average function.
    """

    values = list(values)

    if not values:
        return 0.0

    return sum(values) / len(values)


def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(maximum, value)
    )


def score_from_error(error, tolerance):
    """
    Convert pixel error into a 0-100 score.

    0 pixel error = 100%.

    Error equal to or greater than tolerance = 0%.
    """

    if tolerance <= 0:
        return 0.0

    score = (
        1.0
        -
        min(
            float(error) / float(tolerance),
            1.0
        )
    ) * 100.0

    return clamp(
        score,
        0.0,
        100.0
    )


def load_json(path):
    """
    Load a JSON file.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Required file does not exist:\n{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# ALIGNMENT VALIDATOR
# ---------------------------------------------------------

class AlignmentValidator:

    def __init__(
        self,
        analysis,
        construction
    ):
        self.analysis = analysis
        self.construction = construction

        self.landmarks = (
            analysis["landmarks"]
        )

        self.loomis = (
            construction["loomis"]
        )

        self.measurements = (
            analysis["measurements"]
        )

        self.face_width = float(
            self.measurements["headWidth"]
        )

        # -------------------------------------------------
        # Direct landmark tolerance
        #
        # 5% of face width.
        #
        # This is used for actual landmark anchors.
        # -------------------------------------------------

        self.anchor_tolerance = (
            self.face_width * 0.05
        )

        # -------------------------------------------------
        # Structural tolerance
        #
        # Inferred Loomis geometry is not expected to
        # exactly equal a facial landmark.
        # -------------------------------------------------

        self.structural_tolerance = (
            self.face_width * 0.10
        )

    # =====================================================
    # DIRECT LANDMARK SCORE
    # =====================================================

    def direct_result(
        self,
        name,
        errors
    ):
        error = average(errors)

        score = score_from_error(
            error,
            self.anchor_tolerance
        )

        return {
            "name": name,
            "type": "direct_landmark",
            "errorPixels": round(
                error,
                3
            ),
            "score": round(
                score,
                2
            ),
        }

    # =====================================================
    # STRUCTURAL SCORE
    # =====================================================

    def structural_result(
        self,
        name,
        errors
    ):
        error = average(errors)

        score = score_from_error(
            error,
            self.structural_tolerance
        )

        return {
            "name": name,
            "type": "inferred_structure",
            "errorPixels": round(
                error,
                3
            ),
            "score": round(
                score,
                2
            ),
        }

    # =====================================================
    # CENTER AXIS
    # =====================================================

    def validate_center_axis(self):

        axis = (
            self.loomis["centerAxis"]
        )

        actual_forehead = (
            landmark_point(
                self.landmarks,
                10
            )
        )

        actual_chin = (
            landmark_point(
                self.landmarks,
                152
            )
        )

        errors = [

            distance(
                axis["start"],
                actual_forehead
            ),

            distance(
                axis["end"],
                actual_chin
            ),
        ]

        return self.direct_result(
            "Center axis",
            errors
        )

    # =====================================================
    # EYE PLANE
    # =====================================================

    def validate_eye_plane(self):

        # MediaPipe eye centers.
        #
        # Right eye:
        #   outer = 33
        #   inner = 133
        #
        # Left eye:
        #   inner = 362
        #   outer = 263

        right_outer = (
            landmark_point(
                self.landmarks,
                33
            )
        )

        right_inner = (
            landmark_point(
                self.landmarks,
                133
            )
        )

        left_inner = (
            landmark_point(
                self.landmarks,
                362
            )
        )

        left_outer = (
            landmark_point(
                self.landmarks,
                263
            )
        )

        actual_right_eye = midpoint(
            right_outer,
            right_inner
        )

        actual_left_eye = midpoint(
            left_inner,
            left_outer
        )

        eye_plane = (
            self.loomis["eyePlane"]
        )

        errors = [

            distance(
                eye_plane["start"],
                actual_right_eye
            ),

            distance(
                eye_plane["end"],
                actual_left_eye
            ),
        ]

        return self.direct_result(
            "Eye plane",
            errors
        )

    # =====================================================
    # NOSE
    # =====================================================

    def validate_nose(self):

        nose = (
            self.loomis["nosePlane"]
        )

        actual_root = (
            landmark_point(
                self.landmarks,
                168
            )
        )

        actual_tip = (
            landmark_point(
                self.landmarks,
                4
            )
        )

        actual_left_base = (
            landmark_point(
                self.landmarks,
                48
            )
        )

        actual_right_base = (
            landmark_point(
                self.landmarks,
                278
            )
        )

        errors = [

            distance(
                nose["root"],
                actual_root
            ),

            distance(
                nose["tip"],
                actual_tip
            ),

            distance(
                nose["leftBase"],
                actual_left_base
            ),

            distance(
                nose["rightBase"],
                actual_right_base
            ),
        ]

        return self.direct_result(
            "Nose construction",
            errors
        )

    # =====================================================
    # MOUTH
    # =====================================================

    def validate_mouth(self):

        mouth = (
            self.loomis["mouthPlane"]
        )

        actual_left = (
            landmark_point(
                self.landmarks,
                61
            )
        )

        actual_right = (
            landmark_point(
                self.landmarks,
                291
            )
        )

        mouth_line = (
            mouth["mouthLine"]
        )

        errors = [

            distance(
                mouth_line["start"],
                actual_left
            ),

            distance(
                mouth_line["end"],
                actual_right
            ),
        ]

        return self.direct_result(
            "Mouth construction",
            errors
        )

    # =====================================================
    # CHIN
    # =====================================================

    def validate_chin(self):

        actual_chin = (
            landmark_point(
                self.landmarks,
                152
            )
        )

        construction_chin = (
            self.loomis["jaw"]["chin"]
        )

        error = distance(
            construction_chin,
            actual_chin
        )

        return self.direct_result(
            "Chin",
            [error]
        )

    # =====================================================
    # JAW CONTOUR
    # =====================================================

    def validate_jaw(self):

        contour = (
            self.loomis["jaw"]["actualContour"]
        )

        if not contour:

            return self.direct_result(
                "Jaw contour",
                [self.anchor_tolerance]
            )

        errors = []

        for construction_point in contour:

            index = int(
                construction_point["index"]
            )

            actual = (
                landmark_point(
                    self.landmarks,
                    index
                )
            )

            errors.append(
                distance(
                    construction_point,
                    actual
                )
            )

        return self.direct_result(
            "Jaw contour",
            errors
        )

    # =====================================================
    # CRANIUM
    # =====================================================

    def validate_cranium(self):

        cranium = (
            self.loomis["cranium"]
        )

        center = cranium["center"]

        radius = float(
            cranium["radiusX"]
        )

        # -------------------------------------------------
        # Actual eye center
        # -------------------------------------------------

        right_eye = midpoint(
            landmark_point(
                self.landmarks,
                33
            ),
            landmark_point(
                self.landmarks,
                133
            )
        )

        left_eye = midpoint(
            landmark_point(
                self.landmarks,
                362
            ),
            landmark_point(
                self.landmarks,
                263
            )
        )

        actual_eye_center = midpoint(
            right_eye,
            left_eye
        )

        # -------------------------------------------------
        # 1. Horizontal relationship
        #
        # Cranium center should be approximately centered
        # around the actual eye center.
        # -------------------------------------------------

        horizontal_error = abs(
            center["x"]
            -
            actual_eye_center["x"]
        )

        # -------------------------------------------------
        # 2. Radius relationship
        #
        # A front-facing Loomis cranium diameter should
        # approximately correspond to the detected head
        # width.
        # -------------------------------------------------

        expected_radius = (
            self.face_width / 2.0
        )

        radius_error = abs(
            radius
            -
            expected_radius
        )

        # -------------------------------------------------
        # 3. Vertical relationship
        #
        # Compare the construction center against the
        # detected forehead/eye region rather than
        # demanding that facial landmarks lie on the
        # outer circle.
        # -------------------------------------------------

        forehead = (
            landmark_point(
                self.landmarks,
                10
            )
        )

        eye_offset = (
            actual_eye_center["y"]
            -
            forehead["y"]
        )

        construction_eye_offset = (
            actual_eye_center["y"]
            -
            center["y"]
        )

        vertical_error = abs(
            construction_eye_offset
            -
            eye_offset * 0.42
        )

        errors = [
            horizontal_error,
            radius_error,
            vertical_error,
        ]

        return self.structural_result(
            "Cranium",
            errors
        )

    # =====================================================
    # COMPLETE VALIDATION
    # =====================================================

    def validate(self):

        components = [

            self.validate_cranium(),

            self.validate_center_axis(),

            self.validate_eye_plane(),

            self.validate_nose(),

            self.validate_mouth(),

            self.validate_chin(),

            self.validate_jaw(),
        ]

        # -------------------------------------------------
        # Overall score
        #
        # The direct landmark components are weighted more
        # heavily because they represent actual detected
        # facial coordinates.
        # -------------------------------------------------

        weights = {
            "Cranium": 1.0,
            "Center axis": 1.5,
            "Eye plane": 1.5,
            "Nose construction": 1.5,
            "Mouth construction": 1.5,
            "Chin": 1.0,
            "Jaw contour": 1.5,
        }

        weighted_total = 0.0
        weight_total = 0.0

        for component in components:

            weight = weights.get(
                component["name"],
                1.0
            )

            weighted_total += (
                component["score"]
                *
                weight
            )

            weight_total += weight

        overall_score = (
            weighted_total / weight_total
            if weight_total > 0
            else 0.0
        )

        return {
            "version": "5.0",

            "engine": {
                "landmarkCount": len(
                    self.landmarks
                ),

                "faceWidth": round(
                    self.face_width,
                    3
                ),

                "anchorTolerancePixels": round(
                    self.anchor_tolerance,
                    3
                ),

                "structuralTolerancePixels": round(
                    self.structural_tolerance,
                    3
                ),
            },

            "components": components,

            "overallScore": round(
                overall_score,
                2
            ),
        }


# ---------------------------------------------------------
# REPORT
# ---------------------------------------------------------

def print_report(result):

    print()
    print("=" * 62)
    print(
        "             LOOMIS AI - ALIGNMENT VALIDATION"
    )
    print("=" * 62)

    engine = result["engine"]

    print()
    print(
        f"Landmarks:              "
        f"{engine['landmarkCount']}"
    )

    print(
        f"Face width:             "
        f"{engine['faceWidth']} px"
    )

    print(
        f"Anchor tolerance:       "
        f"{engine['anchorTolerancePixels']} px"
    )

    print(
        f"Structural tolerance:   "
        f"{engine['structuralTolerancePixels']} px"
    )

    print()
    print("COMPONENT ALIGNMENT")
    print("-" * 62)

    for component in result["components"]:

        print(
            f"{component['name']:<24}"
            f"{component['score']:>7.2f}%"
            f"   "
            f"{component['errorPixels']:>8.3f}px"
            f"   "
            f"{component['type']}"
        )

    print()
    print("-" * 62)

    print(
        "OVERALL STRUCTURAL ALIGNMENT: "
        f"{result['overallScore']:.2f}%"
    )

    print("=" * 62)

    print()

    score = result["overallScore"]

    if score >= 95:

        print(
            "STATUS: EXCELLENT"
        )

        print(
            "The current construction is above the "
            "95% structural target."
        )

    elif score >= 90:

        print(
            "STATUS: STRONG"
        )

        print(
            "The construction is close to the "
            "95% structural target."
        )

    elif score >= 80:

        print(
            "STATUS: NEEDS REFINEMENT"
        )

        print(
            "The construction requires additional "
            "geometric correction."
        )

    else:

        print(
            "STATUS: REQUIRES CORRECTION"
        )

        print(
            "The construction is below the desired "
            "alignment target."
        )

    print()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 62)
    print(
        "             LOOMIS AI"
    )
    print(
        "        ALIGNMENT VALIDATOR v5.0"
    )
    print("=" * 62)

    print()
    print(
        f"Analysis:       {ANALYSIS_FILE}"
    )

    print(
        f"Construction:   {CONSTRUCTION_FILE}"
    )

    print()
    print("Loading data...")

    analysis = load_json(
        ANALYSIS_FILE
    )

    construction = load_json(
        CONSTRUCTION_FILE
    )

    # -----------------------------------------------------
    # Basic validation
    # -----------------------------------------------------

    if not analysis.get("success"):
        raise RuntimeError(
            "analysis.json reports that face analysis failed."
        )

    if "landmarks" not in analysis:
        raise RuntimeError(
            "analysis.json does not contain landmarks."
        )

    if "loomis" not in construction:
        raise RuntimeError(
            "construction.json does not contain Loomis geometry."
        )

    landmark_count = len(
        analysis["landmarks"]
    )

    if landmark_count < 478:
        raise RuntimeError(
            f"Expected 478 landmarks, "
            f"but found {landmark_count}."
        )

    print(
        f"Landmarks: {landmark_count}"
    )

    print(
        f"Geometry: v{construction.get('version', 'unknown')}"
    )

    print()
    print("Calculating alignment...")

    validator = AlignmentValidator(
        analysis,
        construction
    )

    result = validator.validate()

    print_report(
        result
    )

    # -----------------------------------------------------
    # Save result
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        "Validation saved:"
    )

    print(
        OUTPUT_FILE
    )

    print()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    main()