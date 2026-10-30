import json
import math
from pathlib import Path

import cv2
import numpy as np


# ============================================================
# LOOMIS AI
# CONSTRUCTION STAGE RENDERER
# ============================================================


class ConstructionStageRenderer:

    def __init__(self, analysis_path, construction_path):

        self.analysis_path = Path(
            analysis_path
        )

        self.construction_path = Path(
            construction_path
        )

        with open(
            self.analysis_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.analysis = json.load(file)

        with open(
            self.construction_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.construction = json.load(file)

        self.landmarks = (
            self.analysis["landmarks"]
        )

        self.loomis = (
            self.construction["loomis"]
        )

        self.stages = (
            self.construction["stages"]
        )

        self.width = (
            self.analysis["image"]["width"]
        )

        self.height = (
            self.analysis["image"]["height"]
        )

    # ========================================================
    # POINT HELPERS
    # ========================================================

    @staticmethod
    def xy(point):

        return (
            int(round(point["x"])),
            int(round(point["y"]))
        )

    def landmark(self, index):

        point = self.landmarks[index]

        return (
            int(round(point["x"])),
            int(round(point["y"]))
        )

    # ========================================================
    # CANVAS
    # ========================================================

    def create_canvas(self):

        return np.full(
            (
                self.height,
                self.width,
                3
            ),
            255,
            dtype=np.uint8
        )

    # ========================================================
    # DRAWING HELPERS
    # ========================================================

    def line(
        self,
        canvas,
        a,
        b,
        color=(40, 40, 40),
        thickness=2
    ):

        cv2.line(
            canvas,
            self.xy(a),
            self.xy(b),
            color,
            thickness,
            cv2.LINE_AA
        )

    def polyline(
        self,
        canvas,
        points,
        color=(40, 40, 40),
        thickness=2,
        closed=False
    ):

        if not points:
            return

        pts = np.array(
            [
                self.xy(point)
                for point in points
            ],
            dtype=np.int32
        )

        cv2.polylines(
            canvas,
            [pts],
            closed,
            color,
            thickness,
            cv2.LINE_AA
        )

    def circle(
        self,
        canvas,
        center,
        radius,
        color=(40, 40, 40),
        thickness=2
    ):

        cv2.circle(
            canvas,
            self.xy(center),
            int(round(radius)),
            color,
            thickness,
            cv2.LINE_AA
        )

    def ellipse(
        self,
        canvas,
        center,
        radius_x,
        radius_y,
        angle=0,
        color=(40, 40, 40),
        thickness=2
    ):

        cv2.ellipse(
            canvas,
            self.xy(center),
            (
                int(round(radius_x)),
                int(round(radius_y))
            ),
            angle,
            0,
            360,
            color,
            thickness,
            cv2.LINE_AA
        )

    # ========================================================
    # TEXT
    # ========================================================

    def title(
        self,
        canvas,
        stage_number,
        stage_name
    ):

        text = (
            f"LOOMIS AI  |  "
            f"STAGE {stage_number}  |  "
            f"{stage_name}"
        )

        cv2.putText(
            canvas,
            text,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (30, 30, 30),
            2,
            cv2.LINE_AA
        )

    def subtitle(
        self,
        canvas,
        text
    ):

        cv2.putText(
            canvas,
            text,
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (90, 90, 90),
            1,
            cv2.LINE_AA
        )

    # ========================================================
    # STAGE 1
    # CRANIUM
    # ========================================================

    def render_cranium(self, canvas):

        cranium = (
            self.loomis["cranium"]
        )

        self.ellipse(
            canvas,
            cranium["center"],
            cranium["radiusX"],
            cranium["radiusY"],
            color=(80, 80, 80),
            thickness=3
        )

        # Very light construction cross
        center = cranium["center"]

        left = {
            "x":
                center["x"]
                -
                cranium["radiusX"],

            "y":
                center["y"],
        }

        right = {
            "x":
                center["x"]
                +
                cranium["radiusX"],

            "y":
                center["y"],
        }

        top = {
            "x":
                center["x"],

            "y":
                center["y"]
                -
                cranium["radiusY"],
        }

        bottom = {
            "x":
                center["x"],

            "y":
                center["y"]
                +
                cranium["radiusY"],
        }

        self.line(
            canvas,
            left,
            right,
            color=(170, 170, 170),
            thickness=1
        )

        self.line(
            canvas,
            top,
            bottom,
            color=(170, 170, 170),
            thickness=1
        )

    # ========================================================
    # STAGE 2
    # CENTER AXIS
    # ========================================================

    def render_axis(self, canvas):

        axis = (
            self.loomis["centerAxis"]
        )

        self.line(
            canvas,
            axis["start"],
            axis["end"],
            color=(60, 60, 60),
            thickness=3
        )

        # Mark the nose root and tip
        cv2.circle(
            canvas,
            self.xy(axis["noseRoot"]),
            5,
            (100, 100, 100),
            -1,
            cv2.LINE_AA
        )

        cv2.circle(
            canvas,
            self.xy(axis["noseTip"]),
            5,
            (100, 100, 100),
            -1,
            cv2.LINE_AA
        )

    # ========================================================
    # STAGE 3
    # EYE PLANE
    # ========================================================

    def render_eye_plane(self, canvas):

        eye_plane = (
            self.loomis["eyePlane"]
        )

        start = eye_plane["start"]
        end = eye_plane["end"]

        self.line(
            canvas,
            start,
            end,
            color=(70, 70, 70),
            thickness=3
        )

        # Continue the plane outward so that the
        # construction reads as a structural plane.
        angle = math.radians(
            eye_plane["angle"]
        )

        length = 90

        dx = math.cos(angle) * length
        dy = math.sin(angle) * length

        extended_start = {
            "x": start["x"] - dx,
            "y": start["y"] - dy
        }

        extended_end = {
            "x": end["x"] + dx,
            "y": end["y"] + dy
        }

        self.line(
            canvas,
            extended_start,
            extended_end,
            color=(130, 130, 130),
            thickness=1
        )

    # ========================================================
    # STAGE 4
    # JAW
    # ========================================================

    def render_jaw(self, canvas):

        jaw = (
            self.loomis["jaw"]
        )

        # Main Loomis jaw construction
        self.line(
            canvas,
            jaw["leftCheek"],
            jaw["leftAttachment"],
            color=(60, 60, 60),
            thickness=3
        )

        self.line(
            canvas,
            jaw["leftAttachment"],
            jaw["chin"],
            color=(60, 60, 60),
            thickness=3
        )

        self.line(
            canvas,
            jaw["rightCheek"],
            jaw["rightAttachment"],
            color=(60, 60, 60),
            thickness=3
        )

        self.line(
            canvas,
            jaw["rightAttachment"],
            jaw["chin"],
            color=(60, 60, 60),
            thickness=3
        )

        # Actual detected jaw contour shown lightly
        # for validation.
        self.polyline(
            canvas,
            jaw["actualContour"],
            color=(190, 190, 190),
            thickness=1
        )

    # ========================================================
    # STAGE 5
    # NOSE
    # ========================================================

    def render_nose(self, canvas):

        nose = (
            self.loomis["nosePlane"]
        )

        # Nose bridge axis
        self.line(
            canvas,
            nose["root"],
            nose["tip"],
            color=(70, 70, 70),
            thickness=3
        )

        # Nose base
        self.line(
            canvas,
            nose["leftBase"],
            nose["rightBase"],
            color=(70, 70, 70),
            thickness=3
        )

        # Structural wedge
        self.line(
            canvas,
            nose["root"],
            nose["leftBase"],
            color=(100, 100, 100),
            thickness=2
        )

        self.line(
            canvas,
            nose["root"],
            nose["rightBase"],
            color=(100, 100, 100),
            thickness=2
        )

        self.line(
            canvas,
            nose["leftBase"],
            nose["tip"],
            color=(110, 110, 110),
            thickness=2
        )

        self.line(
            canvas,
            nose["rightBase"],
            nose["tip"],
            color=(110, 110, 110),
            thickness=2
        )

    # ========================================================
    # STAGE 6
    # MOUTH
    # ========================================================

    def render_mouth(self, canvas):

        mouth = (
            self.loomis["mouthPlane"]
        )

        self.line(
            canvas,
            mouth["mouthLine"]["start"],
            mouth["mouthLine"]["end"],
            color=(70, 70, 70),
            thickness=3
        )

        # Nose → mouth → chin construction axis
        self.line(
            canvas,
            mouth["upperAnchor"],
            mouth["chin"],
            color=(150, 150, 150),
            thickness=1
        )

    # ========================================================
    # ACTUAL FEATURE VALIDATION
    # ========================================================

    def render_actual_features(
        self,
        canvas
    ):

        accurate = (
            self.construction["accurateFace"]
        )

        # ----------------------------------------------------
        # Eyes
        # ----------------------------------------------------

        eyes = accurate["eyes"]

        self.polyline(
            canvas,
            eyes["right"]["points"],
            color=(110, 110, 110),
            thickness=1,
            closed=True
        )

        self.polyline(
            canvas,
            eyes["left"]["points"],
            color=(110, 110, 110),
            thickness=1,
            closed=True
        )

        # ----------------------------------------------------
        # Nose
        # ----------------------------------------------------

        nose = accurate["nose"]

        self.polyline(
            canvas,
            nose["bridge"],
            color=(130, 130, 130),
            thickness=1
        )

        self.polyline(
            canvas,
            nose["leftContour"],
            color=(130, 130, 130),
            thickness=1
        )

        self.polyline(
            canvas,
            nose["rightContour"],
            color=(130, 130, 130),
            thickness=1
        )

        self.polyline(
            canvas,
            nose["lowerContour"],
            color=(130, 130, 130),
            thickness=1
        )

        # ----------------------------------------------------
        # Mouth
        # ----------------------------------------------------

        mouth = accurate["mouth"]

        self.polyline(
            canvas,
            mouth["upperLip"],
            color=(130, 130, 130),
            thickness=1
        )

        self.polyline(
            canvas,
            mouth["lowerLip"],
            color=(130, 130, 130),
            thickness=1
        )

        # ----------------------------------------------------
        # Jaw
        # ----------------------------------------------------

        contour = (
            accurate["faceContour"]["jaw"]
        )

        self.polyline(
            canvas,
            contour,
            color=(130, 130, 130),
            thickness=1
        )

    # ========================================================
    # STAGE RENDERING
    # ========================================================

    def render_stage(
        self,
        stage_number,
        stage_name,
        include_reference=False
    ):

        canvas = self.create_canvas()

        # -----------------------------------------------
        # Loomis construction
        # -----------------------------------------------

        self.render_cranium(
            canvas
        )

        if stage_number >= 2:

            self.render_axis(
                canvas
            )

        if stage_number >= 3:

            self.render_eye_plane(
                canvas
            )

        if stage_number >= 4:

            self.render_jaw(
                canvas
            )

        if stage_number >= 5:

            self.render_nose(
                canvas
            )

        if stage_number >= 6:

            self.render_mouth(
                canvas
            )

        # -----------------------------------------------
        # Optional actual facial geometry
        # -----------------------------------------------

        if include_reference:

            self.render_actual_features(
                canvas
            )

        self.title(
            canvas,
            stage_number,
            stage_name
        )

        self.subtitle(
            canvas,
            "Landmark-driven Loomis construction"
        )

        return canvas

    # ========================================================
    # SAVE ALL STAGES
    # ========================================================

    def render_all(
        self,
        output_directory
    ):

        output_directory = Path(
            output_directory
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        stage_names = {
            1: "CRANIUM",
            2: "CENTER AXIS",
            3: "EYE PLANE",
            4: "JAW",
            5: "NOSE",
            6: "MOUTH",
            7: "COMPLETE CONSTRUCTION",
        }

        created = []

        for number, name in stage_names.items():

            canvas = self.render_stage(
                number,
                name,
                include_reference=False
            )

            output_path = (
                output_directory
                /
                f"stage_{number:02d}_{name.lower().replace(' ', '_')}.png"
            )

            success = cv2.imwrite(
                str(output_path),
                canvas
            )

            if not success:

                raise RuntimeError(
                    f"Could not save:\n"
                    f"{output_path}"
                )

            created.append(
                output_path
            )

        # ------------------------------------------------
        # Validation image
        # ------------------------------------------------

        validation = self.render_stage(
            7,
            "COMPLETE + LANDMARK VALIDATION",
            include_reference=True
        )

        validation_path = (
            output_directory
            /
            "stage_07_landmark_validation.png"
        )

        success = cv2.imwrite(
            str(validation_path),
            validation
        )

        if not success:

            raise RuntimeError(
                f"Could not save:\n"
                f"{validation_path}"
            )

        created.append(
            validation_path
        )

        return created


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("              LOOMIS AI")
    print("       MEMBER 2 - STAGE RENDERER")
    print("=" * 60)

    base_dir = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    analysis_path = (
        base_dir
        /
        "output"
        /
        "analysis.json"
    )

    construction_path = (
        base_dir
        /
        "output"
        /
        "construction.json"
    )

    output_directory = (
        base_dir
        /
        "output"
        /
        "stages"
    )

    print()
    print(
        f"Analysis: {analysis_path}"
    )

    print(
        f"Construction: {construction_path}"
    )

    print()
    print("Loading geometry...")

    renderer = ConstructionStageRenderer(
        analysis_path,
        construction_path
    )

    print(
        "Geometry loaded."
    )

    print()
    print("Rendering 7 construction stages...")

    created = renderer.render_all(
        output_directory
    )

    print()
    print("=" * 60)
    print("              RENDER COMPLETE")
    print("=" * 60)

    print()

    for path in created:

        print(
            f"✓ {path.name}"
        )

    print()
    print(
        f"Output directory:\n"
        f"{output_directory}"
    )

    print()


if __name__ == "__main__":

    main()