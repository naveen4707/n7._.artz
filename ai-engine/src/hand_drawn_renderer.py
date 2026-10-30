import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from graphite_quality import GraphiteQualityEngine, GraphiteStyle


# ============================================================
# LOOMIS AI
# MEMBER 2 - HAND DRAWN GRAPHITE RENDERER
# ============================================================

CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1200

PAPER = (247, 247, 244)

GRAPHITE_DARK = (48, 48, 46)
GRAPHITE = (72, 72, 69)
GRAPHITE_LIGHT = (125, 125, 120)
GRAPHITE_FAINT = (175, 175, 168)

TITLE = (55, 55, 53)
SUBTITLE = (110, 110, 106)


# ============================================================
# BASIC HELPERS
# ============================================================

def point_xy(point):
    """
    Normalize a construction point into an (x, y) tuple.

    Supported formats:
        {"x": 123, "y": 456}
        {"x": 123, "y": 456, "z": 0}
        (123, 456)
        [123, 456]
    """

    if point is None:
        return 0.0, 0.0

    # Dictionary point
    if isinstance(point, dict):
        return (
            float(point.get("x", 0.0)),
            float(point.get("y", 0.0)),
        )

    # Tuple/list point
    if isinstance(point, (tuple, list)):
        if len(point) >= 2:
            return (
                float(point[0]),
                float(point[1]),
            )

    # NumPy-like point
    if hasattr(point, "x") and hasattr(point, "y"):
        return (
            float(point.x),
            float(point.y),
        )

    raise TypeError(
        f"Unsupported point format: {type(point).__name__} -> {point!r}"
    )

def distance(a, b):
    if not a or not b:
        return 0.0

    return math.sqrt(
        ((a[0] - b[0]) ** 2) +
        ((a[1] - b[1]) ** 2)
    )


def midpoint(a, b):
    return (
        (a[0] + b[0]) / 2.0,
        (a[1] + b[1]) / 2.0,
    )


def lerp(a, b, t):
    return (
        a[0] + ((b[0] - a[0]) * t),
        a[1] + ((b[1] - a[1]) * t),
    )


# ============================================================
# HAND-DRAWN STROKE ENGINE
# ============================================================

class GraphiteStrokeEngine:
    """
    M2.3 drawing-quality adapter.

    The geometry code still calls the original stroke/line/curve/ellipse
    interface, but this adapter now adds a controlled pencil hierarchy:

    - faint construction = thin, light, exploratory
    - light construction = visible guide
    - medium construction = structural
    - dark construction = feature/contour emphasis

    The underlying coordinates are never modified.
    """

    def __init__(self, image, seed=42, stage_number=7):
        self.quality = GraphiteQualityEngine(
            image,
            seed=seed,
            style=GraphiteStyle(
                width=1.0,
                wobble=0.44,
                passes=3,
                grain_strength=4,
            ),
        )
        self.image = self.quality.image
        self.draw = self.quality.draw
        self.random = random.Random(seed)
        self.stage_number = stage_number

    def _strength_from_color(self, fill):
        """Map renderer colors to a controlled pencil-pressure hierarchy."""

        if fill == GRAPHITE_DARK:
            return 0.96

        if fill == GRAPHITE:
            return 0.80

        if fill == GRAPHITE_LIGHT:
            return 0.38

        if fill == GRAPHITE_FAINT:
            return 0.16

        if isinstance(fill, tuple) and len(fill) >= 3:
            luminance = (
                0.2126 * fill[0]
                + 0.7152 * fill[1]
                + 0.0722 * fill[2]
            )
            strength = 1.0 - (luminance / 255.0)
            return max(0.12, min(0.95, strength))

        return 0.70

    def _hierarchy(self, fill, width, roughness, passes, opacity):
        """
        Convert the old renderer parameters into natural pencil behavior.

        This intentionally changes appearance only; it does not change points.
        """

        if fill == GRAPHITE_FAINT:
            strength = 0.16
            target_width = 0.52
            target_passes = 1
            wobble = 0.32

        elif fill == GRAPHITE_LIGHT:
            strength = 0.38
            target_width = 0.72
            target_passes = 2
            wobble = 0.38

        elif fill == GRAPHITE_DARK:
            strength = 0.96
            target_width = 1.18
            target_passes = 4
            wobble = 0.48

        else:
            strength = 0.80
            target_width = 0.92
            target_passes = 3
            wobble = 0.44

        # Preserve caller intent while keeping the visual hierarchy stable.
        target_width *= max(0.72, min(1.30, float(width) / 2.0))
        target_passes = max(
            1,
            min(5, max(target_passes, int(passes))),
        )
        wobble = max(
            0.22,
            min(0.95, max(wobble, float(roughness) * 0.42)),
        )

        if opacity < 255:
            strength *= opacity / 255.0

        return strength, target_width, wobble, target_passes

    def jitter_point(self, point, amount):
        return (
            point[0] + self.random.uniform(-amount, amount),
            point[1] + self.random.uniform(-amount, amount),
        )

    def jitter_polyline(self, points, amount):
        return [
            self.jitter_point(point, amount)
            for point in points
        ]

    def stroke(
        self,
        points,
        width=2,
        fill=GRAPHITE,
        roughness=0.8,
        passes=2,
        opacity=255,
    ):
        if not points or len(points) < 2:
            return

        strength, target_width, wobble, target_passes = self._hierarchy(
            fill,
            width,
            roughness,
            passes,
            opacity,
        )

        self.quality.pencil_stroke(
            points,
            strength=strength,
            width=target_width,
            wobble=wobble,
            passes=target_passes,
        )

    def line(
        self,
        start,
        end,
        width=2,
        fill=GRAPHITE,
        roughness=0.8,
        passes=2,
    ):
        self.stroke(
            [start, end],
            width=width,
            fill=fill,
            roughness=roughness,
            passes=passes,
        )

    def ellipse(
        self,
        center,
        radius_x,
        radius_y,
        width=2,
        fill=GRAPHITE,
        roughness=0.8,
        passes=2,
        segments=96,
    ):
        points = []

        for index in range(segments + 1):
            angle = (
                2.0 *
                math.pi *
                index /
                segments
            )

            x = center[0] + (
                math.cos(angle) *
                radius_x
            )

            y = center[1] + (
                math.sin(angle) *
                radius_y
            )

            points.append((x, y))

        self.stroke(
            points,
            width=width,
            fill=fill,
            roughness=roughness,
            passes=passes,
        )

    def curve(
        self,
        points,
        width=2,
        fill=GRAPHITE,
        roughness=0.8,
        passes=2,
    ):
        if not points or len(points) < 2:
            return

        self.stroke(
            points,
            width=width,
            fill=fill,
            roughness=roughness,
            passes=passes,
        )

    def finalize(self):
        """
        Finish the page using the quality engine's surface treatment.
        """

        return self.quality.finalize()


class HandDrawnLoomisRenderer:

    def __init__(
        self,
        construction,
        analysis=None,
        img_path=None,
    ):

        self.construction = construction
        self.analysis = analysis
        self.img_path = img_path

        if self.analysis is None:
            cand = Path(__file__).resolve().parent.parent / "output" / "analysis.json"
            if cand.exists():
                try:
                    with open(cand, "r", encoding="utf-8") as f:
                        self.analysis = json.load(f)
                except Exception:
                    self.analysis = None

        if self.img_path is None:
            ref_cand = Path(__file__).resolve().parent.parent / "input" / "reference.jpg"
            if ref_cand.exists():
                self.img_path = ref_cand

        self.accurate = construction.get(
            "accurateFace",
            {}
        )

        self.loomis = construction.get(
            "loomis",
            {}
        )

        self.face_contour = self.accurate.get(
            "faceContour",
            {}
        )

        self.eyes = self.accurate.get(
            "eyes",
            {}
        )

        self.eyebrows = self.accurate.get(
            "eyebrows",
            {}
        )

        self.nose = self.accurate.get(
            "nose",
            {}
        )

        self.mouth = self.accurate.get(
            "mouth",
            {}
        )

        self.cranium = self.loomis.get(
            "cranium",
            {}
        )

        self.center_axis = self.loomis.get(
            "centerAxis",
            {}
        )

        self.eye_plane = self.loomis.get(
            "eyePlane",
            {}
        )

        self.jaw = self.loomis.get(
            "jaw",
            {}
        )

        self.nose_plane = self.loomis.get(
            "nosePlane",
            {}
        )

        self.mouth_plane = self.loomis.get(
            "mouthPlane",
            {}
        )

        self.source_width = self._get_source_width()
        self.source_height = self._get_source_height()

        self.transform = self._create_transform()

    # ========================================================
    # SOURCE DIMENSIONS
    # ========================================================

    def _get_source_width(self):

        image = self.construction.get(
            "image",
            {}
        )

        if image.get("width"):
            return float(image["width"])

        face_points = self._face_points()

        if face_points:
            return max(
                point[0]
                for point in face_points
            ) + 100

        return 631.0

    def _get_source_height(self):

        image = self.construction.get(
            "image",
            {}
        )

        if image.get("height"):
            return float(image["height"])

        face_points = self._face_points()

        if face_points:
            return max(
                point[1]
                for point in face_points
            ) + 100

        return 858.0

    # ========================================================
    # FACE POINT EXTRACTION
    # ========================================================

    def _face_points(self):

        points = self.face_contour.get("all")

        if not points:
            points = self.face_contour.get("points")

        if not points:
            return []

        result = []

        for point in points:

            xy = point_xy(point)

            if xy:
                result.append(xy)

        return result

    # ========================================================
    # TRANSFORMATION
    # ========================================================

    def _create_transform(self):
        source_w = self.source_width
        source_h = self.source_height
        scale = min(840.0 / max(source_w, 1.0), 1000.0 / max(source_h, 1.0))
        offset_x = (CANVAS_WIDTH - source_w * scale) / 2.0
        offset_y = 115.0

        return {
            "min_x": 0.0,
            "min_y": 0.0,
            "scale": scale,
            "offset_x": offset_x,
            "offset_y": offset_y,
        }

    def transform_point(self, point):

        if not point:
            return None

        scale = self.transform["scale"]
        offset_x = self.transform.get("offset_x", 0.0)
        offset_y = self.transform.get("offset_y", 0.0)

        x = point[0] * scale + offset_x
        y = point[1] * scale + offset_y

        return (x, y)

    def transform_points(self, points):

        result = []

        for point in points:

            xy = point_xy(point)

            if xy:
                result.append(
                    self.transform_point(xy)
                )

        return result

    # ========================================================
    # PAPER
    # ========================================================

    def create_canvas(self):

        image = Image.new(
            "RGB",
            (
                CANVAS_WIDTH,
                CANVAS_HEIGHT
            ),
            PAPER,
        )

        draw = ImageDraw.Draw(image)

        # Very subtle paper grain.
        for _ in range(28000):

            x = random.randint(
                0,
                CANVAS_WIDTH - 1
            )

            y = random.randint(
                0,
                CANVAS_HEIGHT - 1
            )

            value = random.randint(
                235,
                250
            )

            draw.point(
                (x, y),
                fill=(
                    value,
                    value,
                    value,
                ),
            )

        return image

    # ========================================================
    # HEADER
    # ========================================================

    def draw_header(
        self,
        draw,
        stage_number,
        stage_name,
    ):

        draw.text(
            (40, 30),
            f"LOOMIS AI | STAGE {stage_number}",
            fill=TITLE,
        )

        draw.text(
            (40, 62),
            stage_name.upper(),
            fill=TITLE,
        )

        draw.line(
            (40, 105, 960, 105),
            fill=(205, 205, 201),
            width=1,
        )

        draw.text(
            (40, 1140),
            "AI-generated graphite construction",
            fill=SUBTITLE,
        )

    # ========================================================
    # CRANIUM
    # ========================================================

    def draw_cranium(self, engine):
        center = self.cranium.get("center")
        if not center:
            return

        center = self.transform_point(
            point_xy(center)
        )

        radius_x = (
            float(
                self.cranium.get(
                    "radiusX",
                    130
                )
            )
            * self.transform["scale"]
        )

        radius_y = (
            float(
                self.cranium.get(
                    "radiusY",
                    130
                )
            )
            * self.transform["scale"]
        )

        engine.ellipse(
            center,
            radius_x,
            radius_y,
            width=3,
            fill=GRAPHITE,
            roughness=1.2,
            passes=3,
        )

        # Very light secondary construction circle.
        engine.ellipse(
            center,
            radius_x * 0.985,
            radius_y * 0.985,
            width=1,
            fill=GRAPHITE_FAINT,
            roughness=0.6,
            passes=1,
        )

        # Andrew Loomis Signature Side Disc (temporal slice for 3/4 and profile views)
        pose = self.construction.get("pose", {})
        yaw = float(pose.get("yaw", 0.0) or 0.0)
        cx, cy = center
        r = (radius_x + radius_y) * 0.5
        if yaw > 12.0:
            disc_cx = cx - r * 0.42
            disc_cy = cy + r * 0.05
            engine.ellipse((disc_cx, disc_cy), r * 0.35, r * 0.48, width=1, fill=GRAPHITE_FAINT, roughness=0.8, passes=1)
            engine.line((disc_cx, disc_cy - r * 0.44), (disc_cx, disc_cy + r * 0.44), width=1, fill=GRAPHITE_FAINT)
            engine.line((disc_cx - r * 0.30, disc_cy), (disc_cx + r * 0.30, disc_cy), width=1, fill=GRAPHITE_FAINT)
        elif yaw < -12.0:
            disc_cx = cx + r * 0.42
            disc_cy = cy + r * 0.05
            engine.ellipse((disc_cx, disc_cy), r * 0.35, r * 0.48, width=1, fill=GRAPHITE_FAINT, roughness=0.8, passes=1)
            engine.line((disc_cx, disc_cy - r * 0.44), (disc_cx, disc_cy + r * 0.44), width=1, fill=GRAPHITE_FAINT)
            engine.line((disc_cx - r * 0.30, disc_cy), (disc_cx + r * 0.30, disc_cy), width=1, fill=GRAPHITE_FAINT)

    # ========================================================
    # CENTER AXIS
    # ========================================================

    def draw_center_axis(
        self,
        engine,
    ):
        points = self.center_axis.get("points", [])
        if isinstance(points, list) and len(points) >= 3:
            transformed = self.transform_points(points)
            if len(transformed) >= 3:
                engine.curve(
                    transformed,
                    width=2,
                    fill=GRAPHITE_LIGHT,
                    roughness=0.8,
                    passes=2,
                )
                return

        start = self.center_axis.get("start")
        end = self.center_axis.get("end")

        if not start or not end:
            if len(points) >= 2:
                start = points[0]
                end = points[-1]

        if not start or not end:
            return

        start = self.transform_point(
            point_xy(start)
        )

        end = self.transform_point(
            point_xy(end)
        )

        engine.line(
            start,
            end,
            width=2,
            fill=GRAPHITE_LIGHT,
            roughness=1.0,
            passes=2,
        )

    # ========================================================
    # EYE PLANE
    # ========================================================

    def draw_eye_plane(
        self,
        engine,
    ):

        start = self.eye_plane.get("start")
        end = self.eye_plane.get("end")

        if not start or not end:
            return

        start = self.transform_point(
            point_xy(start)
        )

        end = self.transform_point(
            point_xy(end)
        )

        engine.line(
            start,
            end,
            width=2,
            fill=GRAPHITE_LIGHT,
            roughness=1.0,
            passes=2,
        )

        center = self.eye_plane.get("center")

        if center:

            center = self.transform_point(
                point_xy(center)
            )

            engine.ellipse(
                center,
                5,
                5,
                width=1,
                fill=GRAPHITE,
                roughness=0.2,
                passes=1,
            )

    # ========================================================
    # JAW
    # ========================================================

    def draw_jaw(
        self,
        engine,
    ):

        points = self.jaw.get("points")

        if not points:
            points = self.jaw.get(
                "contour"
            )

        if not points:
            points = self.face_contour.get(
                "jaw"
            )

        if not points:
            return

        transformed = self.transform_points(
            points
        )

        if len(transformed) < 2:
            return

        engine.curve(
            transformed,
            width=3,
            fill=GRAPHITE,
            roughness=1.25,
            passes=3,
        )

    # ========================================================
    # NOSE
    # ========================================================

    def draw_nose(
        self,
        engine,
    ):
        nose_data = self.nose
        bridge = nose_data.get("bridge", [])
        if bridge:
            engine.curve(self.transform_points(bridge), width=2, fill=GRAPHITE, roughness=0.8, passes=2)
        l_cnt = nose_data.get("leftContour", [])
        if l_cnt:
            engine.curve(self.transform_points(l_cnt), width=2, fill=GRAPHITE, roughness=0.8, passes=2)
        r_cnt = nose_data.get("rightContour", [])
        if r_cnt:
            engine.curve(self.transform_points(r_cnt), width=2, fill=GRAPHITE, roughness=0.8, passes=2)
        lo_cnt = nose_data.get("lowerContour", [])
        if lo_cnt:
            engine.curve(self.transform_points(lo_cnt), width=2, fill=GRAPHITE, roughness=0.8, passes=2)

    # ========================================================
    # MOUTH
    # ========================================================

    def draw_mouth(
        self,
        engine,
    ):
        mouth = self.mouth
        groups = [
            mouth.get("upperLip"),
            mouth.get("lowerLip"),
            mouth.get("innerUpper"),
            mouth.get("innerLower"),
            mouth.get("outer"),
        ]

        for group in groups:
            if not isinstance(group, list):
                continue
            points = self.transform_points(group)
            if len(points) < 2:
                continue
            engine.curve(
                points,
                width=2,
                fill=GRAPHITE,
                roughness=1.0,
                passes=2,
            )

    # ========================================================
    # EYES
    # ========================================================

    def draw_eyes(
        self,
        engine,
    ):
        if not isinstance(self.eyes, dict):
            return

        for eye_name in ("left", "right"):
            eye = self.eyes.get(eye_name)
            if not isinstance(eye, dict):
                continue

            center = eye.get("center")
            if not center:
                continue

            center_p = self.transform_point(point_xy(center))
            scale = self.transform["scale"]
            width = float(eye.get("width", 30)) * scale
            height = float(eye.get("height", 10)) * scale

            # If eyes are closed, draw horizontal resting seam instead of open ellipse
            if height / max(1.0, width) < 0.18:
                engine.line(
                    (center_p[0] - width * 0.45, center_p[1]),
                    (center_p[0] + width * 0.45, center_p[1]),
                    width=2,
                    fill=GRAPHITE,
                    roughness=0.8,
                    passes=2,
                )
            else:
                engine.ellipse(
                    center_p,
                    width * 0.45,
                    height * 0.70,
                    width=2,
                    fill=GRAPHITE,
                    roughness=1.0,
                    passes=2,
                )

    # ========================================================
    # EYEBROWS
    # ========================================================

    def draw_eyebrows(
        self,
        engine,
    ):

        if not isinstance(
            self.eyebrows,
            dict
        ):
            return

        for side in (
            "left",
            "right",
        ):

            group = self.eyebrows.get(
                side
            )

            if not isinstance(
                group,
                list
            ):
                continue

            points = self.transform_points(
                group
            )

            if len(points) < 2:
                continue

            engine.curve(
                points,
                width=3,
                fill=GRAPHITE,
                roughness=1.3,
                passes=3,
            )

    # ========================================================
    # STAGE RENDERING
    # ========================================================

    def render_stage(
        self,
        stage_number,
        stage_name=None,
    ):
        if stage_name is None:
            stage_name = STAGES.get(stage_number, f"Stage {stage_number}")

        if stage_number == 8:
            from stage_08_eye_construction import Stage8EyeConstruction
            return Stage8EyeConstruction(self.construction).render()

        if stage_number == 9:
            from stage_09_eye_eyelid_construction import Stage09EyeRenderer
            return Stage09EyeRenderer(self.construction).render()

        if stage_number == 10:
            from stage_10_eyebrow_construction import Stage10EyebrowRenderer
            return Stage10EyebrowRenderer(self.construction).render()

        if stage_number == 11:
            from stage_11_nose_construction import Stage11NoseRenderer
            return Stage11NoseRenderer(self.construction).render()

        if stage_number == 12:
            from stage_12_mouth_construction import Stage12MouthRenderer
            return Stage12MouthRenderer(self.construction, self.analysis).render()

        if stage_number == 13:
            from stage_13_cheek_forehead_contours import Stage13CheekForeheadRenderer
            return Stage13CheekForeheadRenderer(self.construction, self.analysis).render()

        if stage_number == 14:
            from stage_14_ear_construction import Stage14EarRenderer
            return Stage14EarRenderer(self.construction, self.analysis).render()

        if stage_number == 15:
            from stage_15_hairline_hair_mass import Stage15HairlineHairMassRenderer
            return Stage15HairlineHairMassRenderer(self.construction, self.analysis, img_path=self.img_path).render()

        if stage_number == 16:
            from stage_16_neck_construction import Stage16NeckRenderer
            return Stage16NeckRenderer(self.construction, self.analysis, img_path=self.img_path).render()

        if stage_number == 17:
            from stage_17_facial_contour_refinement import Stage17FacialContourRenderer
            return Stage17FacialContourRenderer(self.construction, self.analysis, img_path=self.img_path).render()

        if stage_number == 18:
            from stage_18_shadow_structures import Stage18ShadowRenderer
            return Stage18ShadowRenderer(self.construction, self.analysis, img_path=self.img_path).render()

        if stage_number == 19:
            from stage_19_secondary_details import Stage19SecondaryDetailsRenderer
            return Stage19SecondaryDetailsRenderer(self.construction, self.analysis, img_path=self.img_path).render()

        if stage_number == 20:
            from stage_20_final_portrait import Stage20FinalPortraitRenderer
            return Stage20FinalPortraitRenderer(self.construction, self.analysis, img_path=self.img_path).render()

        image = self.create_canvas()

        draw = ImageDraw.Draw(
            image
        )

        engine = GraphiteStrokeEngine(
            image,
            seed=100 + stage_number,
            stage_number=stage_number,
        )

        self.draw_header(
            engine.draw,
            stage_number,
            stage_name,
        )

        # ----------------------------------------------------
        # Stage 1
        # ----------------------------------------------------

        if stage_number >= 1:
            self.draw_cranium(
                engine
            )

        # ----------------------------------------------------
        # Stage 2
        # ----------------------------------------------------

        if stage_number >= 2:
            self.draw_center_axis(
                engine
            )

        # ----------------------------------------------------
        # Stage 3
        # ----------------------------------------------------

        if stage_number >= 3:
            self.draw_eye_plane(
                engine
            )

        # ----------------------------------------------------
        # Stage 4
        # ----------------------------------------------------

        if stage_number >= 4:
            self.draw_jaw(
                engine
            )

        # ----------------------------------------------------
        # Stage 5
        # ----------------------------------------------------

        if stage_number >= 5:
            self.draw_nose(
                engine
            )

        # ----------------------------------------------------
        # Stage 6
        # ----------------------------------------------------

        if stage_number >= 6:
            self.draw_mouth(
                engine
            )

        # ----------------------------------------------------
        # Stage 7
        # ----------------------------------------------------

        if stage_number >= 7:
            self.draw_eyes(
                engine
            )

            self.draw_eyebrows(
                engine
            )

        # Apply the graphite surface treatment after all construction
        # strokes have been drawn. This adds very subtle graphite dust,
        # paper variation, and surface irregularity.
        image = engine.finalize()

        # A tiny blur softens synthetic pixel edges without destroying
        # the underlying construction geometry.
        image = image.filter(
            ImageFilter.GaussianBlur(
                radius=0.12
            )
        )

        return image


# ============================================================
# MAIN
# ============================================================

STAGES = {
    1: "Cranium",
    2: "Center Axis",
    3: "Eye Plane",
    4: "Jaw Construction",
    5: "Nose Construction",
    6: "Mouth Construction",
    7: "Complete Loomis Construction",
    8: "Eye Construction",
    9: "Eyeball and Eyelid Construction",
    10: "Eyebrow Construction",
    11: "Nose Construction",
    12: "Mouth Construction",
    13: "Cheek and Forehead Contours",
    14: "Ear Construction",
    15: "Hairline and Hair Mass",
    16: "Neck and Shoulders Construction",
    17: "Facial Contour Refinement",
    18: "Major Shadow Structures",
    19: "Secondary Details",
    20: "Final Master Graphite Portrait",
}


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Loomis AI Member 2 "
            "Hand-Drawn Graphite Renderer"
        )
    )

    parser.add_argument(
        "--input",
        default=(
            "output/construction.json"
        ),
        help="Construction JSON file.",
    )

    parser.add_argument(
        "--stage",
        type=int,
        default=7,
        choices=range(1, 21),
        help="Stage number to render (1-20).",
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Output image path.",
    )

    args = parser.parse_args()

    input_path = Path(
        args.input
    )

    if not input_path.is_absolute():
        candidates = [
            Path.cwd() / input_path,
            Path(__file__).resolve().parent.parent / input_path,
            Path(__file__).resolve().parent.parent / "output" / "construction.json",
            Path.cwd() / "output" / "construction.json",
            Path.cwd() / "ai-engine" / "output" / "construction.json",
        ]
        resolved = None
        for c in candidates:
            if c.exists():
                resolved = c
                break
        if resolved:
            input_path = resolved
        else:
            input_path = (
                Path.cwd() /
                input_path
            )

    if not input_path.exists():

        raise FileNotFoundError(
            f"Construction JSON not found:\n"
            f"{input_path}"
        )

    print()
    print("=" * 60)
    print("             LOOMIS AI")
    print("     MEMBER 2 - GRAPHITE RENDERER")
    print("=" * 60)
    print()

    print(
        f"Loading construction:\n"
        f"{input_path}"
    )

    construction = load_json(
        input_path
    )

    version = construction.get(
        "version",
        "unknown"
    )

    print(
        f"Geometry version: {version}"
    )

    renderer = HandDrawnLoomisRenderer(
        construction
    )

    stage_name = STAGES[
        args.stage
    ]

    print()
    print(
        f"Rendering Stage "
        f"{args.stage}: "
        f"{stage_name}"
    )

    image = renderer.render_stage(
        args.stage,
        stage_name,
    )

    if args.output:

        output_path = Path(
            args.output
        )

        if not output_path.is_absolute():
            output_path = (
                Path.cwd() /
                output_path
            )

    else:

        output_dir = (
            Path.cwd() /
            "output" /
            "hand_drawn"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            output_dir /
            f"stage_{args.stage:02d}.png"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image.save(
        output_path,
        quality=95,
    )

    print()
    print(
        "Graphite image created:"
    )
    print(
        output_path.resolve()
    )

    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()