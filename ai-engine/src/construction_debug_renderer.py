import argparse
import json
from pathlib import Path

import cv2


class ConstructionDebugRenderer:
    """
    Loomis AI v4.0 construction diagnostic renderer.

    Reads the current construction.json schema:
        accurateFace -> faceContour / eyes / eyebrows / nose / mouth
        loomis       -> cranium / centerAxis / eyePlane / jaw / nosePlane / mouthPlane

    This is a diagnostic overlay renderer, not the final pencil renderer.
    """

    COLORS = {
        "cranium": (255, 180, 0),
        "axis": (0, 255, 255),
        "eyes": (0, 255, 0),
        "eye_plane": (0, 255, 120),
        "eyebrows": (255, 0, 255),
        "contour": (0, 165, 255),
        "nose": (255, 255, 0),
        "mouth": (255, 80, 80),
        "jaw": (0, 140, 255),
        "guide": (180, 180, 180),
        "text": (255, 255, 255),
    }

    def __init__(self, analysis, construction):
        self.analysis = analysis
        self.construction = construction

        if self.construction.get("version") != "4.0":
            raise ValueError(
                "Unsupported construction geometry version: "
                f"{self.construction.get('version')}"
            )

        self.face = self.construction.get("accurateFace", {})
        self.loomis = self.construction.get("loomis", {})

    @staticmethod
    def pt(point):
        if not isinstance(point, dict) or "x" not in point or "y" not in point:
            return None
        return (
            int(round(point["x"])),
            int(round(point["y"])),
        )

    def line(self, image, a, b, color, thickness=2):
        a = self.pt(a)
        b = self.pt(b)
        if a is None or b is None:
            return
        cv2.line(image, a, b, color, thickness, cv2.LINE_AA)

    def polyline(self, image, points, color, thickness=2, closed=False):
        if not isinstance(points, list):
            return

        valid = [self.pt(p) for p in points]
        valid = [p for p in valid if p is not None]

        if len(valid) < 2:
            return

        for a, b in zip(valid, valid[1:]):
            cv2.line(image, a, b, color, thickness, cv2.LINE_AA)

        if closed:
            cv2.line(image, valid[-1], valid[0], color, thickness, cv2.LINE_AA)

    def point(self, image, point, color, radius=4):
        p = self.pt(point)
        if p is None:
            return
        cv2.circle(image, p, radius, color, -1, cv2.LINE_AA)

    def label(self, image, text, position, color, scale=0.55):
        cv2.putText(
            image,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            2,
            cv2.LINE_AA,
        )

    def draw_cranium(self, image):
        cranium = self.loomis.get("cranium", {})
        center = self.pt(cranium.get("center"))
        if center is None:
            return

        rx = int(round(cranium.get("radiusX", 0)))
        ry = int(round(cranium.get("radiusY", 0)))
        if rx <= 0 or ry <= 0:
            return

        color = self.COLORS["cranium"]
        cv2.ellipse(
            image,
            center,
            (rx, ry),
            0,
            0,
            360,
            color,
            2,
            cv2.LINE_AA,
        )
        self.point(image, cranium.get("center"), color, 6)
        self.label(
            image,
            "LOOMIS CRANIUM",
            (center[0] - 65, max(20, center[1] - ry - 12)),
            color,
        )

    def draw_center_axis(self, image):
        axis = self.loomis.get("centerAxis", {})
        points = axis.get("points", [])

        for a, b in zip(points, points[1:]):
            self.line(image, a, b, self.COLORS["axis"], 2)

        for p in points:
            self.point(image, p, self.COLORS["axis"], 4)

        start = self.pt(axis.get("start"))
        if start:
            self.label(
                image,
                "CENTER AXIS",
                (start[0] + 10, start[1] + 20),
                self.COLORS["axis"],
            )

    def draw_eyes(self, image):
        eyes = self.face.get("eyes", {})
        color = self.COLORS["eyes"]

        for side in ("left", "right"):
            eye = eyes.get(side, {})
            points = eye.get("points", [])
            self.polyline(image, points, color, 2)

            center = eye.get("center")
            self.point(image, center, color, 5)

        axis = self.loomis.get("eyePlane", {})
        self.line(
            image,
            axis.get("start"),
            axis.get("end"),
            self.COLORS["eye_plane"],
            3,
        )
        self.point(
            image,
            axis.get("center"),
            self.COLORS["eye_plane"],
            5,
        )

        center = self.pt(axis.get("center"))
        if center:
            self.label(
                image,
                "EYE PLANE",
                (center[0] + 10, center[1] - 10),
                self.COLORS["eye_plane"],
            )

    def draw_eyebrows(self, image):
        eyebrows = self.face.get("eyebrows", {})
        color = self.COLORS["eyebrows"]

        for side in ("left", "right"):
            eyebrow = eyebrows.get(side, {})
            self.polyline(
                image,
                eyebrow.get("points", []),
                color,
                2,
            )

    def draw_face_contour(self, image):
        contour = self.face.get("faceContour", {})
        color = self.COLORS["contour"]

        # v4.0 uses "all" for the complete contour.
        points = contour.get("all", [])
        if not points:
            # Fallback for any older exported geometry.
            points = contour.get("points", [])

        self.polyline(image, points, color, 3, closed=True)

        chin = contour.get("chin")
        self.point(image, chin, color, 6)

        p = self.pt(chin)
        if p:
            self.label(
                image,
                "JAW / CHIN",
                (p[0] + 10, p[1]),
                color,
            )

    def draw_jaw(self, image):
        jaw = self.loomis.get("jaw", {})
        color = self.COLORS["jaw"]

        # The v4 jaw contains actualContour plus left/right structural paths.
        self.polyline(
            image,
            jaw.get("actualContour", []),
            color,
            2,
        )
        self.polyline(
            image,
            jaw.get("leftPath", []),
            color,
            2,
        )
        self.polyline(
            image,
            jaw.get("rightPath", []),
            color,
            2,
        )

        for name in ("leftAttachment", "rightAttachment", "leftCheek",
                     "rightCheek", "chin"):
            self.point(image, jaw.get(name), color, 4)

    def draw_nose(self, image):
        nose = self.face.get("nose", {})
        color = self.COLORS["nose"]

        # Current v4 accurateFace.nose uses these contour names.
        self.polyline(image, nose.get("bridge", []), color, 3)
        self.polyline(image, nose.get("leftContour", []), color, 2)
        self.polyline(image, nose.get("rightContour", []), color, 2)
        self.polyline(image, nose.get("lowerContour", []), color, 2)

        # Also draw the structural nose plane.
        plane = self.loomis.get("nosePlane", {})
        self.line(
            image,
            plane.get("root"),
            plane.get("tip"),
            color,
            2,
        )
        self.line(
            image,
            plane.get("leftBase"),
            plane.get("rightBase"),
            color,
            2,
        )

        for name in ("root", "center", "tip", "leftBase", "rightBase"):
            self.point(image, nose.get(name), color, 5)

        tip = self.pt(nose.get("tip"))
        if tip:
            self.label(
                image,
                "NOSE",
                (tip[0] + 10, tip[1]),
                color,
            )

    def draw_mouth(self, image):
        mouth = self.face.get("mouth", {})
        color = self.COLORS["mouth"]

        # IMPORTANT:
        # construction v4.0 calls these fields:
        #   innerUpper
        #   innerLower
        # not innerUpperLip / innerLowerLip.
        self.polyline(image, mouth.get("upperLip", []), color, 2)
        self.polyline(image, mouth.get("lowerLip", []), color, 2)
        self.polyline(image, mouth.get("innerUpper", []), color, 2)
        self.polyline(image, mouth.get("innerLower", []), color, 2)

        self.point(image, mouth.get("leftCorner"), color, 4)
        self.point(image, mouth.get("rightCorner"), color, 4)
        self.point(image, mouth.get("center"), color, 5)

        # Structural mouth-plane guides.
        plane = self.loomis.get("mouthPlane", {})
        mouth_line = plane.get("mouthLine", {})
        self.line(
            image,
            mouth_line.get("start"),
            mouth_line.get("end"),
            color,
            2,
        )
        self.line(
            image,
            plane.get("upperAnchor"),
            plane.get("chin"),
            self.COLORS["guide"],
            1,
        )

        center = self.pt(mouth.get("center"))
        if center:
            self.label(
                image,
                "MOUTH",
                (center[0] + 10, center[1]),
                color,
            )

    def render(self, reference_path, output_path):
        image = cv2.imread(str(reference_path))
        if image is None:
            raise ValueError(f"Could not read image:\n{reference_path}")

        canvas = image.copy()

        self.draw_cranium(canvas)
        self.draw_center_axis(canvas)
        self.draw_eyes(canvas)
        self.draw_eyebrows(canvas)
        self.draw_face_contour(canvas)
        self.draw_jaw(canvas)
        self.draw_nose(canvas)
        self.draw_mouth(canvas)

        height, width = canvas.shape[:2]

        self.label(
            canvas,
            "LOOMIS AI - LANDMARK DEBUG v4.0",
            (20, height - 20),
            self.COLORS["text"],
            0.65,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not cv2.imwrite(str(output_path), canvas):
            raise RuntimeError(f"Could not save debug image:\n{output_path}")

        return output_path


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Loomis AI v4.0 construction diagnostic renderer."
    )

    parser.add_argument("--image", default="input/reference.jpg")
    parser.add_argument("--analysis", default="output/analysis.json")
    parser.add_argument("--construction", default="output/construction.json")
    parser.add_argument("--output", default="output/construction_debug.png")

    return parser.parse_args()


def main():
    args = parse_arguments()

    image_path = Path(args.image)
    analysis_path = Path(args.analysis)
    construction_path = Path(args.construction)
    output_path = Path(args.output)

    print("=" * 60)
    print("              LOOMIS AI")
    print("      ACCURATE LANDMARK DEBUG")
    print("=" * 60)

    print()
    print("Loading analysis...")
    analysis = load_json(analysis_path)
    print(f"Landmarks: {len(analysis.get('landmarks', []))}")

    print()
    print("Loading construction...")
    construction = load_json(construction_path)
    print(f"Geometry version: {construction.get('version')}")

    print()
    print("Rendering...")

    renderer = ConstructionDebugRenderer(
        analysis,
        construction,
    )

    result = renderer.render(
        image_path,
        output_path,
    )

    print()
    print("Debug image created:")
    print(result.resolve())
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
