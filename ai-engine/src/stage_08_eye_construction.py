import argparse
import json
import math
from pathlib import Path

from PIL import ImageFilter

from hand_drawn_renderer import (
    HandDrawnLoomisRenderer,
    GraphiteStrokeEngine,
)


# ============================================================
# LOOMIS AI
# MEMBER 2 - STAGE 8 EYE CONSTRUCTION ENGINE
# ============================================================
#
# Stage 8 extends the validated 7-stage Loomis construction.
#
# It reads ONLY the existing construction geometry:
#   accurateFace.eyes
#   loomis.eyePlane
#
# No landmark indices are re-invented here.
# No image-generation API is used.
#
# The renderer adds:
#   - eye sockets
#   - upper/lower eyelid construction
#   - eyeball ellipses
#   - iris construction circles/ellipses
#   - iris cross-axis guides
#   - light searching/construction lines
#
# Geometry remains deterministic and landmark-driven.
# ============================================================


AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = AI_ENGINE_DIR / "output"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
DEFAULT_OUTPUT = HAND_DRAWN_DIR / "stage_08.png"


def load_construction(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Construction JSON not found:\n{path}\n\n"
            "Run construction_main.py first."
        )

    with open(path, "r", encoding="utf-8") as file:
        construction = json.load(file)

    if construction.get("version") != "4.0":
        raise ValueError(
            "Unsupported construction geometry version: "
            f"{construction.get('version')}. Expected 4.0."
        )

    if not isinstance(construction.get("accurateFace"), dict):
        raise ValueError("construction.json is missing accurateFace.")

    if not isinstance(construction.get("loomis"), dict):
        raise ValueError("construction.json is missing loomis.")

    return construction


def point_xy(point):
    """Accept the project's normal point dictionaries safely."""
    if not isinstance(point, dict):
        return None

    try:
        return float(point["x"]), float(point["y"])
    except (KeyError, TypeError, ValueError):
        return None


def rotate_ellipse(center, radius_x, radius_y, angle_degrees, samples=96):
    """Return points for a rotated ellipse in source-image coordinates."""
    cx, cy = center
    angle = math.radians(angle_degrees)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    points = []

    for index in range(samples + 1):
        theta = 2.0 * math.pi * index / samples
        local_x = radius_x * math.cos(theta)
        local_y = radius_y * math.sin(theta)

        x = cx + (local_x * cos_a) - (local_y * sin_a)
        y = cy + (local_x * sin_a) + (local_y * cos_a)

        points.append((x, y))

    return points


def line_endpoints(center, half_length, angle_degrees):
    """Return endpoints of a line through center at the requested angle."""
    angle = math.radians(angle_degrees)
    dx = math.cos(angle) * half_length
    dy = math.sin(angle) * half_length

    return (
        (center[0] - dx, center[1] - dy),
        (center[0] + dx, center[1] + dy),
    )


def eye_data(eyes, side):
    group = eyes.get(side)

    if not isinstance(group, dict):
        raise ValueError(f"accurateFace.eyes.{side} is missing.")

    points = group.get("points", [])
    center = point_xy(group.get("center"))
    bbox = group.get("boundingBox", {})

    if not isinstance(points, list) or len(points) < 4:
        raise ValueError(
            f"accurateFace.eyes.{side}.points does not contain enough points."
        )

    if center is None:
        raise ValueError(
            f"accurateFace.eyes.{side}.center is missing."
        )

    if not isinstance(bbox, dict):
        raise ValueError(
            f"accurateFace.eyes.{side}.boundingBox is missing."
        )

    width = float(bbox.get("width", 0.0))
    height = float(bbox.get("height", 0.0))

    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid eye bounding box for {side}: "
            f"width={width}, height={height}"
        )

    normalized = []
    for point in points:
        xy = point_xy(point)
        if xy is not None:
            normalized.append(xy)

    if len(normalized) < 4:
        raise ValueError(
            f"accurateFace.eyes.{side}.points contains invalid points."
        )

    return {
        "points": normalized,
        "center": center,
        "width": width,
        "height": height,
        "indices": group.get("landmarkIndices", []),
    }


def split_lids(points, indices):
    """
    Split the existing eye contour into upper/lower paths.

    The current LoomisGeometry arrays already contain the anatomical
    corner indices. We use those existing indices instead of creating
    a new landmark map.
    """
    if not isinstance(indices, list) or len(indices) != len(points):
        midpoint = max(2, len(points) // 2)
        return points[:midpoint], points[midpoint:]

    target = 133 if 133 in indices else 263 if 263 in indices else None

    if target is None:
        midpoint = max(2, len(points) // 2)
        return points[:midpoint], points[midpoint:]

    split_at = indices.index(target)

    upper = points[:split_at + 1]
    lower = points[split_at:]

    if len(upper) < 2 or len(lower) < 2:
        midpoint = max(2, len(points) // 2)
        return points[:midpoint], points[midpoint:]

    return upper, lower


class Stage8EyeConstruction:
    def __init__(self, construction):
        self.construction = construction
        self.accurate = construction["accurateFace"]
        self.eyes = self.accurate["eyes"]
        self.eye_plane = construction["loomis"]["eyePlane"]

        self.renderer = HandDrawnLoomisRenderer(construction)

    def transform_points(self, points):
        result = []

        for point in points:
            transformed = self.renderer.transform_point(point)
            if transformed is not None:
                result.append(transformed)

        return result

    def transform_point(self, point):
        return self.renderer.transform_point(point)

    def draw_eye_construction(self, engine, side):
        data = eye_data(self.eyes, side)

        points = self.transform_points(data["points"])
        center = self.transform_point(data["center"])

        if len(points) < 4 or center is None:
            return

        scale = self.renderer.transform["scale"]

        width = data["width"] * scale
        height = data["height"] * scale

        eye_plane_angle = float(
            self.eye_plane.get("angle", 0.0)
        )

        # --------------------------------------------------------
        # 1. Outer eye socket
        # --------------------------------------------------------
        engine.quality.ghost_stroke(
            points + [points[0]],
            strength=0.15,
            width=0.62,
            closed=False,
        )

        # Slightly enlarged searching ellipse.
        socket_rx = max(width * 0.56, 3.0)
        socket_ry = max(height * 0.62, 2.0)

        socket = rotate_ellipse(
            center,
            socket_rx,
            socket_ry,
            eye_plane_angle,
        )

        engine.quality.ghost_stroke(
            socket,
            strength=0.13,
            width=0.58,
            closed=True,
        )

        # --------------------------------------------------------
        # 2. Upper and lower eyelid construction
        # --------------------------------------------------------
        upper_source, lower_source = split_lids(
            data["points"],
            data["indices"],
        )

        upper = self.transform_points(upper_source)
        lower = self.transform_points(lower_source)

        if len(upper) >= 2:
            engine.quality.structural_stroke(
                upper,
                strength=0.72,
                width=1.05,
                closed=False,
            )

        if len(lower) >= 2:
            engine.quality.structural_stroke(
                lower,
                strength=0.58,
                width=0.95,
                closed=False,
            )

        is_closed = (height / max(1.0, width)) < 0.18 or bool(self.construction.get("pose", {}).get("eyesClosed", False))

        # --------------------------------------------------------
        # 3. Eyeball construction
        # --------------------------------------------------------
        # Larger than the visible opening, so the stage teaches
        # spherical eye construction rather than tracing the eyelids.
        eyeball_rx = max(width * 0.47, 3.5)
        eyeball_ry = max(height * 0.86, 3.5)

        eyeball = rotate_ellipse(
            center,
            eyeball_rx,
            eyeball_ry,
            eye_plane_angle,
        )

        engine.quality.construction_stroke(
            eyeball,
            strength=0.25 if is_closed else 0.30,
            width=0.72 if is_closed else 0.78,
            closed=True,
        )

        if is_closed:
            # For closed eyelids, an artist constructs the resting seam and supratarsal fold.
            # No iris, pupil, or open crosshairs are drawn over closed eyelids!
            if len(upper) >= 2:
                engine.quality.structural_stroke(
                    upper,
                    strength=0.85,
                    width=1.15,
                    closed=False,
                )
                # Gentle supratarsal crease above closed lid
                crease_pts = []
                nx = math.sin(math.radians(eye_plane_angle))
                ny = -math.cos(math.radians(eye_plane_angle))
                for i, p in enumerate(upper):
                    t = i / max(1, len(upper) - 1)
                    off = (height * 0.35 + 2.0) * math.sin(t * math.pi)
                    crease_pts.append((p[0] + nx * off, p[1] + ny * off))
                engine.quality.construction_stroke(
                    crease_pts,
                    strength=0.35,
                    width=0.70,
                    closed=False,
                )
            return

        # --------------------------------------------------------
        # 4. Eyeball cross construction (Open eyes only)
        # --------------------------------------------------------
        horizontal_start, horizontal_end = line_endpoints(
            center,
            eyeball_rx * 0.92,
            eye_plane_angle,
        )

        vertical_start, vertical_end = line_endpoints(
            center,
            eyeball_ry * 0.92,
            eye_plane_angle + 90.0,
        )

        engine.quality.construction_axis(
            horizontal_start,
            horizontal_end,
            strength=0.20,
            width=0.65,
        )

        engine.quality.construction_axis(
            vertical_start,
            vertical_end,
            strength=0.18,
            width=0.62,
        )

        # --------------------------------------------------------
        # 5. Iris construction (Open eyes only)
        # --------------------------------------------------------
        iris_rx = max(
            min(width * 0.19, eyeball_rx * 0.42),
            2.0,
        )
        iris_ry = max(
            min(height * 0.38, eyeball_ry * 0.55),
            2.0,
        )

        iris = rotate_ellipse(
            center,
            iris_rx,
            iris_ry,
            eye_plane_angle,
        )

        engine.quality.construction_stroke(
            iris,
            strength=0.42,
            width=0.82,
            closed=True,
        )

        # Iris center crosshair.
        iris_h_start, iris_h_end = line_endpoints(
            center,
            iris_rx * 0.90,
            eye_plane_angle,
        )

        iris_v_start, iris_v_end = line_endpoints(
            center,
            iris_ry * 0.90,
            eye_plane_angle + 90.0,
        )

        engine.quality.construction_axis(
            iris_h_start,
            iris_h_end,
            strength=0.24,
            width=0.58,
        )

        engine.quality.construction_axis(
            iris_v_start,
            iris_v_end,
            strength=0.22,
            width=0.56,
        )

        # Small pupil construction circle.
        pupil_radius = max(
            min(iris_rx, iris_ry) * 0.28,
            1.2,
        )

        pupil = rotate_ellipse(
            center,
            pupil_radius,
            pupil_radius,
            0.0,
            samples=64,
        )

        engine.quality.ghost_stroke(
            pupil,
            strength=0.24,
            width=0.62,
            closed=True,
        )

    def render(self):
        image = self.renderer.create_canvas()

        engine = GraphiteStrokeEngine(
            image,
            seed=108,
            stage_number=8,
        )

        # Rebuild the complete validated Stage 7 page first.
        self.renderer.draw_header(
            engine.draw,
            8,
            "Eye Construction",
        )

        self.renderer.draw_cranium(engine)
        self.renderer.draw_center_axis(engine)
        self.renderer.draw_eye_plane(engine)
        self.renderer.draw_jaw(engine)
        self.renderer.draw_nose(engine)
        self.renderer.draw_mouth(engine)
        self.renderer.draw_eyes(engine)
        self.renderer.draw_eyebrows(engine)

        # Stage 8 additions.
        self.draw_eye_construction(engine, "right")
        self.draw_eye_construction(engine, "left")

        # Apply the graphite/paper finish once, after all Stage 8 marks.
        image = engine.finalize()

        image = image.filter(
            ImageFilter.GaussianBlur(radius=0.10)
        )

        return image


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Loomis AI - Stage 8 Eye Construction"
    )

    parser.add_argument(
        "--input",
        default=str(CONSTRUCTION_FILE),
        help="Path to construction.json.",
    )

    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output PNG path.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    construction_path = Path(args.input)
    output_path = Path(args.output)

    if not construction_path.is_absolute():
        construction_path = Path.cwd() / construction_path

    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    print("=" * 60)
    print("              LOOMIS AI")
    print("       MEMBER 2 - STAGE 8")
    print("        EYE CONSTRUCTION")
    print("=" * 60)
    print()
    print(f"Construction: {construction_path}")
    print(f"Output:       {output_path}")
    print()

    construction = load_construction(construction_path)

    print("Geometry version: 4.0")
    print("Reading accurateFace.eyes...")
    print("Reading loomis.eyePlane...")
    print("Building Stage 8 eye construction...")
    print()

    renderer = Stage8EyeConstruction(construction)
    image = renderer.render()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image.save(
        output_path,
        quality=95,
    )

    print("=" * 60)
    print("SUCCESS")
    print("=" * 60)
    print()
    print("Stage 8 created:")
    print(output_path.resolve())
    print()
    print("Added:")
    print("  [OK] Right eye socket")
    print("  [OK] Left eye socket")
    print("  [OK] Upper eyelid construction")
    print("  [OK] Lower eyelid construction")
    print("  [OK] Eyeball ellipses")
    print("  [OK] Iris construction guides")
    print("  [OK] Light cross-construction")
    print("  [OK] Graphite quality rendering")
    print()


if __name__ == "__main__":
    main()
