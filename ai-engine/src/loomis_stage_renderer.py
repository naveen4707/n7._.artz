"""
LOOMIS AI
Progressive Loomis Construction Renderer v4.2

Reads:
    output/construction.json

Generates:
    output/loomis/stage_01.png
    output/loomis/stage_02.png
    output/loomis/stage_03.png
    output/loomis/stage_04.png
    output/loomis/stage_05.png
    output/loomis/stage_06.png
    output/loomis/stage_07.png

Important:
    This renderer does not perform face analysis.
    It renders the already validated v4.0 geometry.
"""

import json
import math
from pathlib import Path

import cv2
import numpy as np


# ============================================================
# PATHS
# ============================================================

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = AI_ENGINE_DIR / "output"

CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"

LOOMIS_DIR = OUTPUT_DIR / "loomis"


# ============================================================
# CANVAS
# ============================================================

CANVAS_WIDTH = 900
CANVAS_HEIGHT = 1100

PAPER = (248, 247, 243)

GRAPHITE_DARK = (48, 48, 48)
GRAPHITE = (75, 75, 75)
GRAPHITE_MEDIUM = (105, 105, 105)
GRAPHITE_LIGHT = (145, 145, 145)
GUIDE = (190, 190, 190)


# ============================================================
# GEOMETRY HELPERS
# ============================================================

def xy(point):
    """
    Convert a geometry point dictionary into (x, y).
    """

    if not isinstance(point, dict):
        return None

    if "x" not in point or "y" not in point:
        return None

    try:
        return (
            float(point["x"]),
            float(point["y"]),
        )
    except (TypeError, ValueError):
        return None


def points_from_sequence(sequence):
    """
    Convert a list of geometry dictionaries into coordinates.
    """

    if not isinstance(sequence, list):
        return []

    result = []

    for item in sequence:

        point = xy(item)

        if point is not None:
            result.append(point)

    return result


def unique_points(points):
    """
    Remove duplicate coordinates while preserving order.
    """

    result = []

    for point in points:

        duplicate = False

        for existing in result:

            if (
                abs(point[0] - existing[0]) < 0.5
                and
                abs(point[1] - existing[1]) < 0.5
            ):
                duplicate = True
                break

        if not duplicate:
            result.append(point)

    return result


def distance(a, b):

    return math.hypot(
        b[0] - a[0],
        b[1] - a[1],
    )


def midpoint(a, b):

    return (
        (a[0] + b[0]) / 2.0,
        (a[1] + b[1]) / 2.0,
    )


def extend_line(start, end, amount):

    dx = end[0] - start[0]
    dy = end[1] - start[1]

    length = math.hypot(dx, dy)

    if length < 0.001:
        return start, end

    ux = dx / length
    uy = dy / length

    return (
        (
            start[0] - ux * amount,
            start[1] - uy * amount,
        ),
        (
            end[0] + ux * amount,
            end[1] + uy * amount,
        ),
    )


# ============================================================
# RENDERER
# ============================================================

class LoomisStageRenderer:

    def __init__(self, construction):

        self.construction = construction

        self.accurate_face = construction.get(
            "accurateFace",
            {}
        )

        self.loomis = construction.get(
            "loomis",
            {}
        )

        self.stages = construction.get(
            "stages",
            {}
        )

        # Current reference image:
        # 631 x 858
        #
        # We use these values from the current project.
        self.source_width = 631
        self.source_height = 858

        self.scale = min(
            CANVAS_WIDTH / self.source_width,
            CANVAS_HEIGHT / self.source_height,
        )

        rendered_width = (
            self.source_width * self.scale
        )

        rendered_height = (
            self.source_height * self.scale
        )

        self.offset_x = (
            CANVAS_WIDTH - rendered_width
        ) / 2

        self.offset_y = (
            CANVAS_HEIGHT - rendered_height
        ) / 2

        self.canvas = None

    # ========================================================
    # COORDINATE CONVERSION
    # ========================================================

    def transform(self, point):

        return (
            int(
                round(
                    point[0] * self.scale
                    +
                    self.offset_x
                )
            ),
            int(
                round(
                    point[1] * self.scale
                    +
                    self.offset_y
                )
            ),
        )

    def transform_points(self, points):

        return [
            self.transform(point)
            for point in points
        ]

    # ========================================================
    # CANVAS
    # ========================================================

    def create_canvas(self):

        return np.full(
            (
                CANVAS_HEIGHT,
                CANVAS_WIDTH,
                3,
            ),
            PAPER,
            dtype=np.uint8,
        )

    # ========================================================
    # DRAWING
    # ========================================================

    def line(
        self,
        start,
        end,
        color=GRAPHITE,
        thickness=2,
    ):

        if start is None or end is None:
            return

        cv2.line(
            self.canvas,
            start,
            end,
            color,
            thickness,
            cv2.LINE_AA,
        )

    def polyline(
        self,
        points,
        color=GRAPHITE,
        thickness=2,
        closed=False,
    ):

        if len(points) < 2:
            return

        for i in range(
            len(points) - 1
        ):

            self.line(
                points[i],
                points[i + 1],
                color,
                thickness,
            )

        if closed:

            self.line(
                points[-1],
                points[0],
                color,
                thickness,
            )

    def circle(
        self,
        center,
        radius,
        color=GRAPHITE,
        thickness=2,
    ):

        cv2.circle(
            self.canvas,
            center,
            int(round(radius)),
            color,
            thickness,
            cv2.LINE_AA,
        )

    def ellipse(
        self,
        center,
        radius_x,
        radius_y,
        color=GRAPHITE,
        thickness=2,
    ):

        cv2.ellipse(
            self.canvas,
            center,
            (
                max(
                    1,
                    int(round(radius_x))
                ),
                max(
                    1,
                    int(round(radius_y))
                ),
            ),
            0,
            0,
            360,
            color,
            thickness,
            cv2.LINE_AA,
        )

    # ========================================================
    # TEXT
    # ========================================================

    def text(
        self,
        value,
        position,
        size=0.65,
        color=GRAPHITE_DARK,
    ):

        cv2.putText(
            self.canvas,
            value,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            size,
            color,
            1,
            cv2.LINE_AA,
        )

    def header(
        self,
        stage_number,
        title,
    ):

        self.text(
            f"LOOMIS AI | STAGE {stage_number}",
            (35, 45),
            0.65,
            GRAPHITE_DARK,
        )

        self.text(
            title,
            (35, 75),
            0.9,
            GRAPHITE_DARK,
        )

        cv2.line(
            self.canvas,
            (35, 92),
            (
                CANVAS_WIDTH - 35,
                92,
            ),
            GUIDE,
            1,
            cv2.LINE_AA,
        )

    # ========================================================
    # STAGE 1
    # ========================================================

    def draw_cranium(self):

        cranium = self.loomis.get(
            "cranium",
            {}
        )

        center = xy(
            cranium.get("center")
        )

        if center is None:
            return

        radius_x = float(
            cranium.get(
                "radiusX",
                130
            )
        )

        radius_y = float(
            cranium.get(
                "radiusY",
                radius_x
            )
        )

        center_canvas = self.transform(
            center
        )

        radius_x_canvas = (
            radius_x * self.scale
        )

        radius_y_canvas = (
            radius_y * self.scale
        )

        # Main cranial sphere
        self.ellipse(
            center_canvas,
            radius_x_canvas,
            radius_y_canvas,
            GRAPHITE_DARK,
            3,
        )

        # Very light second construction stroke
        self.ellipse(
            center_canvas,
            radius_x_canvas - 2,
            radius_y_canvas + 2,
            GRAPHITE_LIGHT,
            1,
        )

    # ========================================================
    # STAGE 2
    # ========================================================

    def draw_center_axis(self):

        axis = self.loomis.get(
            "centerAxis",
            {}
        )

        start = xy(
            axis.get("start")
        )

        end = xy(
            axis.get("end")
        )

        if start is None or end is None:
            return

        # Keep the line close to the construction.
        #
        # The previous renderer extended this too far,
        # producing an unnatural instructional drawing.

        extended_start, extended_end = extend_line(
            start,
            end,
            35,
        )

        self.line(
            self.transform(
                extended_start
            ),
            self.transform(
                extended_end
            ),
            GRAPHITE,
            2,
        )

    # ========================================================
    # STAGE 3
    # ========================================================

    def draw_eye_plane(self):

        eye_plane = self.loomis.get(
            "eyePlane",
            {}
        )

        start = xy(
            eye_plane.get("start")
        )

        end = xy(
            eye_plane.get("end")
        )

        if start is None or end is None:
            return

        # Extend moderately beyond the cranium.
        extended_start, extended_end = extend_line(
            start,
            end,
            35,
        )

        self.line(
            self.transform(
                extended_start
            ),
            self.transform(
                extended_end
            ),
            GRAPHITE,
            2,
        )

        center = xy(
            eye_plane.get("center")
        )

        if center is not None:

            self.circle(
                self.transform(center),
                5,
                GRAPHITE_MEDIUM,
                -1,
            )

    # ========================================================
    # SIDE PLANES
    # ========================================================

    def draw_side_planes(self):

        side_planes = self.loomis.get(
            "sidePlanes",
            {}
        )

        left = side_planes.get(
            "left",
            {}
        )

        right = side_planes.get(
            "right",
            {}
        )

        # Left plane
        left_upper = xy(
            left.get("upper")
        )

        left_inner = xy(
            left.get("inner")
        )

        left_lower = xy(
            left.get("lower")
        )

        if (
            left_upper
            and left_inner
            and left_lower
        ):

            self.line(
                self.transform(
                    left_upper
                ),
                self.transform(
                    left_inner
                ),
                GRAPHITE_LIGHT,
                1,
            )

            self.line(
                self.transform(
                    left_inner
                ),
                self.transform(
                    left_lower
                ),
                GRAPHITE_LIGHT,
                1,
            )

        # Right plane
        right_upper = xy(
            right.get("upper")
        )

        right_inner = xy(
            right.get("inner")
        )

        right_lower = xy(
            right.get("lower")
        )

        if (
            right_upper
            and right_inner
            and right_lower
        ):

            self.line(
                self.transform(
                    right_upper
                ),
                self.transform(
                    right_inner
                ),
                GRAPHITE_LIGHT,
                1,
            )

            self.line(
                self.transform(
                    right_inner
                ),
                self.transform(
                    right_lower
                ),
                GRAPHITE_LIGHT,
                1,
            )

    # ========================================================
    # STAGE 4 — JAW
    # ========================================================

    def draw_jaw(self):

        jaw = self.loomis.get(
            "jaw",
            {}
        )

        # ----------------------------------------------------
        # Actual jaw contour
        # ----------------------------------------------------

        actual_contour = points_from_sequence(
            jaw.get("actualContour")
        )

        actual_contour = unique_points(
            actual_contour
        )

        if len(actual_contour) >= 2:

            self.polyline(
                self.transform_points(
                    actual_contour
                ),
                GRAPHITE_DARK,
                3,
            )

        # ----------------------------------------------------
        # Structural left jaw path
        # ----------------------------------------------------

        left_path = points_from_sequence(
            jaw.get("leftPath")
        )

        if len(left_path) >= 2:

            self.polyline(
                self.transform_points(
                    left_path
                ),
                GRAPHITE,
                2,
            )

        # ----------------------------------------------------
        # Structural right jaw path
        # ----------------------------------------------------

        right_path = points_from_sequence(
            jaw.get("rightPath")
        )

        if len(right_path) >= 2:

            self.polyline(
                self.transform_points(
                    right_path
                ),
                GRAPHITE,
                2,
            )

    # ========================================================
    # STAGE 5 — NOSE
    # ========================================================

    def draw_nose(self):

        nose = self.accurate_face.get(
            "nose",
            {}
        )

        # ----------------------------------------------------
        # Nose bridge
        # ----------------------------------------------------

        bridge = points_from_sequence(
            nose.get("bridge")
        )

        if len(bridge) >= 2:

            self.polyline(
                self.transform_points(
                    bridge
                ),
                GRAPHITE,
                2,
            )

        # ----------------------------------------------------
        # Left contour
        # ----------------------------------------------------

        left_contour = points_from_sequence(
            nose.get("leftContour")
        )

        if len(left_contour) >= 2:

            self.polyline(
                self.transform_points(
                    left_contour
                ),
                GRAPHITE,
                2,
            )

        # ----------------------------------------------------
        # Right contour
        # ----------------------------------------------------

        right_contour = points_from_sequence(
            nose.get("rightContour")
        )

        if len(right_contour) >= 2:

            self.polyline(
                self.transform_points(
                    right_contour
                ),
                GRAPHITE,
                2,
            )

        # ----------------------------------------------------
        # Lower nose contour
        # ----------------------------------------------------

        lower_contour = points_from_sequence(
            nose.get("lowerContour")
        )

        if len(lower_contour) >= 2:

            self.polyline(
                self.transform_points(
                    lower_contour
                ),
                GRAPHITE,
                2,
            )

        # ----------------------------------------------------
        # Loomis nose plane
        # ----------------------------------------------------

        nose_plane = self.loomis.get(
            "nosePlane",
            {}
        )

        root = xy(
            nose_plane.get("root")
        )

        tip = xy(
            nose_plane.get("tip")
        )

        left_base = xy(
            nose_plane.get("leftBase")
        )

        right_base = xy(
            nose_plane.get("rightBase")
        )

        if root and tip:

            self.line(
                self.transform(root),
                self.transform(tip),
                GRAPHITE_LIGHT,
                1,
            )

        if left_base and right_base:

            self.line(
                self.transform(left_base),
                self.transform(right_base),
                GRAPHITE_LIGHT,
                1,
            )

    # ========================================================
    # STAGE 6 — MOUTH
    # ========================================================

    def draw_mouth(self):

        mouth = self.accurate_face.get(
            "mouth",
            {}
        )

        # ----------------------------------------------------
        # Upper lip
        # ----------------------------------------------------

        upper = points_from_sequence(
            mouth.get("upperLip")
        )

        if len(upper) >= 2:

            self.polyline(
                self.transform_points(
                    upper
                ),
                GRAPHITE,
                2,
            )

        # ----------------------------------------------------
        # Lower lip
        # ----------------------------------------------------

        lower = points_from_sequence(
            mouth.get("lowerLip")
        )

        if len(lower) >= 2:

            self.polyline(
                self.transform_points(
                    lower
                ),
                GRAPHITE,
                2,
            )

        # ----------------------------------------------------
        # Inner upper lip
        # ----------------------------------------------------

        inner_upper = points_from_sequence(
            mouth.get("innerUpper")
        )

        if len(inner_upper) >= 2:

            self.polyline(
                self.transform_points(
                    inner_upper
                ),
                GRAPHITE_MEDIUM,
                1,
            )

        # ----------------------------------------------------
        # Inner lower lip
        # ----------------------------------------------------

        inner_lower = points_from_sequence(
            mouth.get("innerLower")
        )

        if len(inner_lower) >= 2:

            self.polyline(
                self.transform_points(
                    inner_lower
                ),
                GRAPHITE_MEDIUM,
                1,
            )

        # ----------------------------------------------------
        # Loomis mouth plane
        # ----------------------------------------------------

        mouth_plane = self.loomis.get(
            "mouthPlane",
            {}
        )

        upper_anchor = xy(
            mouth_plane.get(
                "upperAnchor"
            )
        )

        mouth_center = xy(
            mouth_plane.get(
                "mouthCenter"
            )
        )

        chin = xy(
            mouth_plane.get(
                "chin"
            )
        )

        if (
            upper_anchor
            and chin
        ):

            self.line(
                self.transform(
                    upper_anchor
                ),
                self.transform(
                    chin
                ),
                GRAPHITE_LIGHT,
                1,
            )

        if mouth_center:

            self.circle(
                self.transform(
                    mouth_center
                ),
                3,
                GRAPHITE_LIGHT,
                -1,
            )

    # ========================================================
    # EYES
    # ========================================================

    def draw_eye(
        self,
        eye,
    ):

        points = points_from_sequence(
            eye.get("points")
        )

        if len(points) < 2:
            return

        self.polyline(
            self.transform_points(
                points
            ),
            GRAPHITE_DARK,
            2,
            closed=True,
        )

        center = xy(
            eye.get("center")
        )

        if center:

            box = eye.get(
                "boundingBox",
                {}
            )

            width = float(
                box.get(
                    "width",
                    20
                )
            )

            height = float(
                box.get(
                    "height",
                    10
                )
            )

            center_canvas = self.transform(
                center
            )

            self.ellipse(
                center_canvas,
                width * self.scale * 0.48,
                height * self.scale * 0.42,
                GRAPHITE_LIGHT,
                1,
            )

    def draw_eyes(self):

        eyes = self.accurate_face.get(
            "eyes",
            {}
        )

        right = eyes.get(
            "right",
            {}
        )

        left = eyes.get(
            "left",
            {}
        )

        if right:
            self.draw_eye(right)

        if left:
            self.draw_eye(left)

    # ========================================================
    # EYEBROWS
    # ========================================================

    def draw_eyebrows(self):

        eyebrows = self.accurate_face.get(
            "eyebrows",
            {}
        )

        right = eyebrows.get(
            "right",
            {}
        )

        left = eyebrows.get(
            "left",
            {}
        )

        right_points = points_from_sequence(
            right.get("points")
        )

        left_points = points_from_sequence(
            left.get("points")
        )

        if len(right_points) >= 2:

            self.polyline(
                self.transform_points(
                    right_points
                ),
                GRAPHITE_DARK,
                2,
            )

        if len(left_points) >= 2:

            self.polyline(
                self.transform_points(
                    left_points
                ),
                GRAPHITE_DARK,
                2,
            )

    # ========================================================
    # STAGE RENDERING
    # ========================================================

    def render_stage(
        self,
        stage_number,
    ):

        self.canvas = self.create_canvas()

        titles = {
            1: "CRANIUM",
            2: "CENTER AXIS",
            3: "EYE PLANE",
            4: "JAW CONSTRUCTION",
            5: "NOSE CONSTRUCTION",
            6: "MOUTH CONSTRUCTION",
            7: "COMPLETE LOOMIS CONSTRUCTION",
        }

        self.header(
            stage_number,
            titles[stage_number],
        )

        # ----------------------------------------------------
        # Stage 1
        # ----------------------------------------------------

        self.draw_cranium()

        # ----------------------------------------------------
        # Stage 2
        # ----------------------------------------------------

        if stage_number >= 2:

            self.draw_center_axis()

        # ----------------------------------------------------
        # Stage 3
        # ----------------------------------------------------

        if stage_number >= 3:

            self.draw_eye_plane()

        # ----------------------------------------------------
        # Stage 4
        # ----------------------------------------------------

        if stage_number >= 4:

            self.draw_side_planes()

            self.draw_jaw()

        # ----------------------------------------------------
        # Stage 5
        # ----------------------------------------------------

        if stage_number >= 5:

            self.draw_nose()

        # ----------------------------------------------------
        # Stage 6
        # ----------------------------------------------------

        if stage_number >= 6:

            self.draw_mouth()

        # ----------------------------------------------------
        # Stage 7
        # ----------------------------------------------------

        if stage_number >= 7:

            self.draw_eyes()

            self.draw_eyebrows()

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        self.text(
            "Landmark-driven Loomis construction",
            (
                35,
                CANVAS_HEIGHT - 30,
            ),
            0.48,
            GRAPHITE_LIGHT,
        )

        return self.canvas


# ============================================================
# LOAD JSON
# ============================================================

def load_construction():

    if not CONSTRUCTION_FILE.exists():

        raise FileNotFoundError(
            "construction.json not found:\n"
            f"{CONSTRUCTION_FILE}\n\n"
            "Run construction_main.py first."
        )

    with open(
        CONSTRUCTION_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("              LOOMIS AI")
    print("      PROGRESSIVE STAGE RENDERER")
    print("=" * 60)

    print()
    print("Loading construction geometry...")

    construction = load_construction()

    print(
        "Geometry version:",
        construction.get(
            "version",
            "unknown"
        ),
    )

    print(
        "Coordinate system:",
        construction.get(
            "engine",
            {}
        ).get(
            "coordinateSystem",
            "unknown"
        ),
    )

    renderer = LoomisStageRenderer(
        construction
    )

    LOOMIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("Rendering stages...")
    print()

    for stage_number in range(
        1,
        8,
    ):

        image = renderer.render_stage(
            stage_number
        )

        output_file = (
            LOOMIS_DIR
            /
            f"stage_{stage_number:02d}.png"
        )

        success = cv2.imwrite(
            str(output_file),
            image,
        )

        if not success:

            raise RuntimeError(
                f"Could not save:\n"
                f"{output_file}"
            )

        print(
            f"[OK] Stage {stage_number}: "
            f"{output_file}"
        )

    print()
    print("=" * 60)
    print("SUCCESS")
    print("=" * 60)
    print()
    print(
        "Generated 7 Loomis construction stages."
    )
    print()
    print(
        "Output folder:"
    )
    print(
        LOOMIS_DIR.resolve()
    )
    print()


if __name__ == "__main__":
    main()