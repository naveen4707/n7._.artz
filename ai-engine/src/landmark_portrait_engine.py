"""
LOOMIS AI — LANDMARK PORTRAIT ENGINE
Accurate feature extraction and rendering from all 478 MediaPipe face-mesh landmarks
and computer-vision photograph analysis.

This engine is the foundation for stages 8–20 in the redesigned pipeline.
Every feature (eyes, brows, nose, lips, jaw, hairline, bindi, hair, jewelry, saree)
is derived purely from measured landmark coordinates and CV analysis of the reference portrait.
NO awkward spidery radial lines, NO comb-tooth eyebrows, NO wireframe artifacts.
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw

Point = Tuple[float, float]


# ─────────────────────────────────────────────────────────────
# MEDIAPIPE FACE MESH LANDMARK GROUPS
# ─────────────────────────────────────────────────────────────

FACE_OVAL = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361,
    288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
    150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,
    67, 109,
]

LEFT_EYE_UPPER  = [33, 246, 161, 160, 159, 158, 157, 173, 133]
LEFT_EYE_LOWER  = [33, 7,   163, 144, 145, 153, 154, 155, 133]
LEFT_EYE_OUTER  = 33
LEFT_EYE_INNER  = 133
LEFT_IRIS       = 468

RIGHT_EYE_UPPER = [263, 466, 388, 387, 386, 385, 384, 398, 362]
RIGHT_EYE_LOWER = [263, 249, 390, 373, 374, 380, 381, 382, 362]
RIGHT_EYE_OUTER = 263
RIGHT_EYE_INNER = 362
RIGHT_IRIS      = 473

L_BROW_LOWER = [46,  53,  52,  65,  55]
L_BROW_UPPER = [70,  63, 105,  66, 107]

R_BROW_LOWER = [276, 283, 282, 295, 285]
R_BROW_UPPER = [300, 293, 334, 296, 336]

NOSE_BRIDGE     = [168, 6,  197, 195,  5,  4]
NOSE_TIP        = 4
NOSE_LEFT_WING  = [49, 48, 64,  98,  97]
NOSE_RIGHT_WING = [279, 278, 294, 327, 326]

UPPER_LIP_OUTER = [61, 185, 40, 39, 37,  0, 267, 269, 270, 409, 291]
LOWER_LIP_OUTER = [61, 146,  91, 181, 84, 17, 314, 405, 321, 375, 291]
UPPER_LIP_INNER = [78, 191, 80, 81,  82, 13, 312, 311, 310, 415, 308]
LOWER_LIP_INNER = [78,  95, 88, 178, 87, 14, 317, 402, 318, 324, 308]

MOUTH_LEFT  = 61
MOUTH_RIGHT = 291
CHIN = 152
HAIRLINE = [21, 54, 103, 67, 109, 10, 338, 297, 332, 284, 251]


def _catmull_rom_chain(pts: List[Point], samples: int = 5) -> List[Point]:
    """Catmull-Rom spline through the list of control points."""
    if len(pts) < 2:
        return pts
    result: List[Point] = []
    padded = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(padded) - 2):
        p0, p1, p2, p3 = padded[i - 1], padded[i], padded[i + 1], padded[i + 2]
        for s in range(samples):
            t = s / float(samples)
            t2, t3 = t * t, t * t * t
            x = 0.5 * (
                2 * p1[0] + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                2 * p1[1] + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            result.append((x, y))
    result.append(pts[-1])
    return result


def _circle_pts(center: Point, radius: float, n: int = 24) -> List[Point]:
    cx, cy = center
    return [
        (cx + radius * math.cos(2 * math.pi * i / n),
         cy + radius * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]


def _draw_white_dot(image: Image.Image, cx: float, cy: float, r: float) -> None:
    draw = ImageDraw.Draw(image)
    x0, y0 = int(cx - r), int(cy - r)
    x1, y1 = int(cx + r), int(cy + r)
    draw.ellipse([x0, y0, x1, y1], fill=(255, 255, 255))


class LandmarkPortraitEngine:
    """Landmark-accurate portrait rendering engine."""

    def __init__(
        self,
        construction: Dict[str, Any],
        analysis: Dict[str, Any],
        img_path: Optional[Any] = None,
    ) -> None:
        from pathlib import Path
        from hand_drawn_renderer import HandDrawnLoomisRenderer
        from dynamic_contour_extractor import DynamicContourExtractor

        self.construction = construction
        self.analysis = analysis
        self.lms: List[Dict] = analysis.get("landmarks", [])
        self.base = HandDrawnLoomisRenderer(construction)
        self.scale = self.base.transform["scale"]

        if img_path is None:
            img_path = Path(__file__).resolve().parent.parent / "input" / "reference.jpg"
        self.img_path = Path(img_path)
        self.extractor = DynamicContourExtractor(
            self.img_path, analysis, self.base.transform_point, self.scale
        )

    def lm(self, idx: int) -> Optional[Point]:
        if idx < 0 or idx >= len(self.lms):
            return None
        p = self.lms[idx]
        return self.base.transform_point((p["x"], p["y"]))

    def lm_pts(self, indices: List[int]) -> List[Point]:
        return [self.lm(i) for i in indices if self.lm(i) is not None]

    def spline(self, pts: List[Point], samples: int = 6) -> List[Point]:
        return _catmull_rom_chain(pts, samples)

    # ── Feature extraction ────────────────────────────────────

    def get_face_oval(self) -> List[Point]:
        pts = self.lm_pts(FACE_OVAL)
        if len(pts) < 6:
            return pts
        # Jawline from left ear through chin to right ear
        return self.spline(pts[8:29], 5)

    def get_eye_data(self, side: str) -> Dict:
        if side == "left":
            upper_raw = self.lm_pts(LEFT_EYE_UPPER)
            lower_raw = self.lm_pts(LEFT_EYE_LOWER)
            outer = self.lm(LEFT_EYE_OUTER)
            inner = self.lm(LEFT_EYE_INNER)
            iris_c = self.lm(LEFT_IRIS)
            p_up_mid = self.lm(159)
            p_lo_mid = self.lm(145)
        else:
            upper_raw = self.lm_pts(RIGHT_EYE_UPPER)
            lower_raw = self.lm_pts(RIGHT_EYE_LOWER)
            outer = self.lm(RIGHT_EYE_OUTER)
            inner = self.lm(RIGHT_EYE_INNER)
            iris_c = self.lm(RIGHT_IRIS)
            p_up_mid = self.lm(386)
            p_lo_mid = self.lm(374)

        if not (outer and inner):
            return {}

        eye_width = math.hypot(inner[0] - outer[0], inner[1] - outer[1])
        if p_up_mid and p_lo_mid:
            eye_height = math.hypot(p_lo_mid[0] - p_up_mid[0], p_lo_mid[1] - p_up_mid[1])
        else:
            eye_height = eye_width * 0.25

        ear = eye_height / max(1.0, eye_width)
        pose_closed = self.analysis.get("pose", {}).get("eyesClosed", False)
        is_closed = pose_closed or (ear < 0.17)

        if iris_c is None:
            iris_c = ((outer[0] + inner[0]) / 2.0, (outer[1] + inner[1]) / 2.0)

        iris_r = eye_width * 0.30
        pupil_r = iris_r * 0.42

        return {
            "side": side,
            "outer": outer,
            "inner": inner,
            "iris_center": iris_c,
            "iris_r": iris_r,
            "pupil_r": pupil_r,
            "eye_width": eye_width,
            "eye_height": eye_height,
            "ear": ear,
            "is_closed": is_closed,
            "upper_lid": self.spline(upper_raw, 5) if len(upper_raw) >= 3 else upper_raw,
            "lower_lid": self.spline(lower_raw, 5) if len(lower_raw) >= 3 else lower_raw,
        }

    def get_brow_data(self, side: str) -> Dict:
        if side == "left":
            lower = self.lm_pts(L_BROW_LOWER)
            upper = self.lm_pts(L_BROW_UPPER)
        else:
            lower = self.lm_pts(R_BROW_LOWER)
            upper = self.lm_pts(R_BROW_UPPER)
        return {
            "lower": self.spline(lower, 5) if len(lower) >= 3 else lower,
            "upper": self.spline(upper, 5) if len(upper) >= 3 else upper,
        }

    def get_nose_data(self) -> Dict:
        return {
            "bridge":     self.spline(self.lm_pts(NOSE_BRIDGE), 4),
            "tip":        self.lm(NOSE_TIP),
            "left_wing":  self.spline(self.lm_pts(NOSE_LEFT_WING), 4),
            "right_wing": self.spline(self.lm_pts(NOSE_RIGHT_WING), 4),
            "nostril_l":  self.lm(98),
            "nostril_r":  self.lm(327),
        }

    def get_lip_data(self) -> Dict:
        uo = self.lm_pts(UPPER_LIP_OUTER)
        lo = self.lm_pts(LOWER_LIP_OUTER)
        ui = self.lm_pts(UPPER_LIP_INNER)
        li = self.lm_pts(LOWER_LIP_INNER)
        # Sinuous closure line from corner 61 through 13 to corner 291
        closure = self.lm_pts([61, 78, 191, 80, 81, 13, 312, 311, 308, 291])
        return {
            "upper_outer": self.spline(uo, 5) if len(uo) >= 4 else uo,
            "lower_outer": self.spline(lo, 5) if len(lo) >= 4 else lo,
            "upper_inner": self.spline(ui, 5) if len(ui) >= 4 else ui,
            "lower_inner": self.spline(li, 5) if len(li) >= 4 else li,
            "closure":     self.spline(closure, 5) if len(closure) >= 4 else closure,
            "mouth_left":  self.lm(MOUTH_LEFT),
            "mouth_right": self.lm(MOUTH_RIGHT),
        }

    def get_chin(self) -> Optional[Point]:
        return self.lm(CHIN)

    def get_hairline(self) -> List[Point]:
        pts = self.lm_pts(HAIRLINE)
        return self.spline(pts, 5) if len(pts) >= 4 else pts

    def get_bindi(self) -> Optional[Point]:
        mark = self.extractor.detect_forehead_mark()
        return mark[0] if mark else None

    # ── Drawing methods ────────────────────────────────────────

    def draw_loomis_underdrawing(self, engine, strength_factor: float = 0.6) -> None:
        """
        Draw subtle, light 2H Loomis construction underdrawing:
          - Cranium sphere
          - Vertical center face axis
          - Horizontal brow/eye axis
          - Temporal side plane ellipse
        Clean ghost strokes that guide the composition without cluttering features.
        """
        cranium = self.construction.get("loomis", {}).get("cranium", {})
        center = cranium.get("center")
        if center:
            cx, cy = self.base.transform_point((center["x"], center["y"]))
            rx = float(cranium.get("radiusX", 130)) * self.scale
            ry = float(cranium.get("radiusY", 130)) * self.scale
            r_avg = (rx + ry) * 0.5
            engine.quality.ghost_stroke(
                _circle_pts((cx, cy), r_avg, 36),
                strength=0.22 * strength_factor,
                width=0.75,
                closed=True,
            )
            # Secondary concentric guide
            engine.quality.ghost_stroke(
                _circle_pts((cx, cy), r_avg * 0.98, 32),
                strength=0.12 * strength_factor,
                width=0.55,
                closed=True,
            )

        # Loomis side disc (temporal cut on near side for 3/4 & profile views)
        yaw = float(self.analysis.get("pose", {}).get("yaw", 0.0) or 0.0)
        if center:
            cx, cy = self.base.transform_point((center["x"], center["y"]))
            r = r_avg
            if yaw > 12.0:
                # 3/4 or Profile Right: side plane visible on left
                disc_cx = cx - r * 0.42
                disc_cy = cy + r * 0.05
                disc_pts = [
                    (disc_cx + r * 0.35 * math.cos(math.radians(a)),
                     disc_cy + r * 0.48 * math.sin(math.radians(a)))
                    for a in range(0, 360, 10)
                ]
                engine.quality.ghost_stroke(disc_pts, strength=0.20 * strength_factor, width=0.65, closed=True)
                engine.quality.ghost_stroke([(disc_cx, disc_cy - r * 0.44), (disc_cx, disc_cy + r * 0.44)], strength=0.14 * strength_factor, width=0.55)
                engine.quality.ghost_stroke([(disc_cx - r * 0.30, disc_cy), (disc_cx + r * 0.30, disc_cy)], strength=0.14 * strength_factor, width=0.55)
            elif yaw < -12.0:
                # 3/4 or Profile Left: side plane visible on right
                disc_cx = cx + r * 0.42
                disc_cy = cy + r * 0.05
                disc_pts = [
                    (disc_cx + r * 0.35 * math.cos(math.radians(a)),
                     disc_cy + r * 0.48 * math.sin(math.radians(a)))
                    for a in range(0, 360, 10)
                ]
                engine.quality.ghost_stroke(disc_pts, strength=0.20 * strength_factor, width=0.65, closed=True)
                engine.quality.ghost_stroke([(disc_cx, disc_cy - r * 0.44), (disc_cx, disc_cy + r * 0.44)], strength=0.14 * strength_factor, width=0.55)
                engine.quality.ghost_stroke([(disc_cx - r * 0.30, disc_cy), (disc_cx + r * 0.30, disc_cy)], strength=0.14 * strength_factor, width=0.55)

        # 3D central axis: follows cranial sphere curve down through nose root, tip, and chin
        axis_lms = [10, 168, 6, 4, 13, 152]
        axis_pts = [self.lm(i) for i in axis_lms if self.lm(i) is not None]
        if len(axis_pts) >= 4:
            smooth_axis = self.spline(axis_pts, 4)
            engine.quality.ghost_stroke(
                smooth_axis,
                strength=0.20 * strength_factor,
                width=0.65,
            )
        else:
            top_pt = self.lm(10)
            chin_pt = self.lm(152)
            if top_pt and chin_pt:
                engine.quality.ghost_stroke(
                    [(top_pt[0], top_pt[1] - 30 * self.scale),
                     (chin_pt[0], chin_pt[1] + 20 * self.scale)],
                    strength=0.18 * strength_factor,
                    width=0.65,
                )

        # Horizontal brow line guide (curving with head pitch)
        lb = self.lm(107)
        rb = self.lm(336)
        if lb and rb:
            dx = rb[0] - lb[0]
            dy = rb[1] - lb[1]
            p_left = (lb[0] - 0.28 * dx, lb[1] - 0.28 * dy)
            p_right = (rb[0] + 0.28 * dx, rb[1] + 0.28 * dy)
            engine.quality.ghost_stroke(
                [p_left, p_right],
                strength=0.16 * strength_factor,
                width=0.60,
            )

    def draw_face_oval(self, engine, strength: float = 0.92, width: float = 1.45) -> None:
        pts = self.get_face_oval()
        if pts:
            engine.quality.structural_stroke(pts, strength=strength, width=width)

    def draw_hairline(self, engine, strength: float = 0.60, width: float = 0.90) -> None:
        hl = self.get_hairline()
        if hl:
            engine.quality.construction_stroke(hl, strength=strength, width=width)

    def draw_bindi(self, engine) -> None:
        """Draw forehead mark (bindi, beauty mark, or mole) ONLY if dynamically detected in photo."""
        mark = self.extractor.detect_forehead_mark()
        if mark:
            bc, br = mark
            engine.quality.draw.ellipse([bc[0] - br, bc[1] - br, bc[0] + br, bc[1] + br], fill=(22, 20, 19))
            engine.quality.structural_stroke(_circle_pts(bc, br, 16), strength=0.98, width=1.1, closed=True)

    def draw_eye(self, engine, side: str, iris_strength: float = 0.94) -> None:
        """Draw clean, almond eye without radial lines or wireframes; respects closed vs open eyelids."""
        data = self.get_eye_data(side)
        if not data:
            return

        ul = data["upper_lid"]
        ll = data["lower_lid"]
        iris_c = data["iris_center"]
        iris_r = data["iris_r"]
        pupil_r = data["pupil_r"]
        outer_p = data["outer"]
        inner_p = data["inner"]
        is_closed = data.get("is_closed", False)

        if is_closed:
            # ─────────────────────────────────────────────────────
            # CLOSED OR DOWNCAST EYE (Peaceful, resting eyelid margin)
            # ─────────────────────────────────────────────────────
            # 1. Supratarsal crease above closed lid
            if ul:
                crease = _catmull_rom_chain([(p[0], p[1] - 5.5 * self.scale) for p in ul], 4)
                engine.quality.ghost_stroke(crease, strength=0.45, width=0.75)

            # 2. Main resting eyelid seam (deep velvet lash margin)
            if ul:
                engine.quality.structural_stroke(ul, strength=0.98, width=2.20)

            # 3. Delicate downward-sweeping eyelashes resting from the seam
            if ul and len(ul) >= 4:
                for idx in range(1, len(ul) - 1, 2):
                    p_lash = ul[idx]
                    lash_len = 4.5 * self.scale
                    engine.quality.pencil_stroke([
                        p_lash,
                        (p_lash[0], p_lash[1] + lash_len)
                    ], strength=0.72, width=0.85, passes=1)

            # 4. Subtle lower lid resting contour
            if ll:
                engine.quality.ghost_stroke(ll, strength=0.35, width=0.70)

            # 5. Medial tear duct
            engine.quality.ghost_stroke([
                inner_p,
                (inner_p[0] + (1 if side == 'left' else -1) * 2.5 * self.scale, inner_p[1] + 1 * self.scale)
            ], strength=0.45, width=0.70)

        else:
            # ─────────────────────────────────────────────────────
            # OPEN EYE (Almond eye with iris, pupil, and catchlight)
            # ─────────────────────────────────────────────────────
            # Supratarsal crease
            crease = _catmull_rom_chain([(p[0], p[1] - 8.0 * self.scale) for p in ul], 4)
            engine.quality.ghost_stroke(crease, strength=0.50, width=0.80)

            # Iris: dark graphite filled circle
            engine.quality.draw.ellipse(
                [iris_c[0] - iris_r, iris_c[1] - iris_r, iris_c[0] + iris_r, iris_c[1] + iris_r],
                fill=(48, 45, 42)
            )
            # Limbal ring
            iris_pts = _circle_pts(iris_c, iris_r, n=32)
            engine.quality.structural_stroke(iris_pts, strength=iris_strength, width=1.20, closed=True)

            # Pupil: solid dark 6B graphite
            engine.quality.draw.ellipse(
                [iris_c[0] - pupil_r, iris_c[1] - pupil_r, iris_c[0] + pupil_r, iris_c[1] + pupil_r],
                fill=(14, 13, 12)
            )
            pupil_pts = _circle_pts(iris_c, pupil_r, n=20)
            engine.quality.structural_stroke(pupil_pts, strength=0.98, width=1.25, closed=True)

            # Specular catchlight: crisp pure white highlight dot
            catch_x = iris_c[0] - iris_r * 0.28
            catch_y = iris_c[1] - iris_r * 0.32
            catch_r = max(iris_r * 0.18, 2.4)
            _draw_white_dot(engine.quality.image, catch_x, catch_y, catch_r)

            # Upper eyelid: dark kohl line
            if ul:
                engine.quality.structural_stroke(ul, strength=0.98, width=2.45)
            # Lower eyelid: delicate stroke
            if ll:
                engine.quality.construction_stroke(ll, strength=0.68, width=0.95)

            # Subtle winged outer flick
            flick_dir = -1 if side == 'left' else 1
            engine.quality.structural_stroke([
                outer_p,
                (outer_p[0] + flick_dir * 6.5 * self.scale, outer_p[1] - 3.8 * self.scale),
            ], strength=0.90, width=1.25)

            # Medial tear duct
            engine.quality.ghost_stroke([
                inner_p,
                (inner_p[0] + (1 if side == 'left' else -1) * 3 * self.scale, inner_p[1] + 1 * self.scale)
            ], strength=0.55, width=0.80)

    def draw_eyebrow(self, engine, side: str) -> None:
        """Draw natural arched eyebrow with soft directional flow (NO comb ticks!)."""
        data = self.get_brow_data(side)
        lower = data["lower"]
        upper = data["upper"]

        if lower:
            engine.quality.structural_stroke(lower, strength=0.96, width=1.55)
        if upper:
            engine.quality.structural_stroke(upper, strength=0.82, width=1.10)

        # Soft interior flow strokes following hair growth direction
        if lower and upper and len(lower) == len(upper):
            for off in [-0.25, 0.0, 0.25]:
                mid = [
                    ((1 - (0.5 + off)) * l[0] + (0.5 + off) * u[0],
                     (1 - (0.5 + off)) * l[1] + (0.5 + off) * u[1])
                    for u, l in zip(upper, lower)
                ]
                engine.quality.pencil_stroke(mid, strength=0.88, width=1.25, passes=2)

    def draw_nose(self, engine) -> None:
        data = self.get_nose_data()
        tip = data["tip"]
        l_wing = data["left_wing"]
        r_wing = data["right_wing"]
        nostril_l = data["nostril_l"]
        nostril_r = data["nostril_r"]

        if l_wing:
            engine.quality.structural_stroke(l_wing, strength=0.84, width=1.15)
        if r_wing:
            engine.quality.structural_stroke(r_wing, strength=0.84, width=1.15)

        if nostril_l and nostril_r:
            # Dark crescent nostril accents
            engine.quality.structural_stroke([
                (nostril_l[0] - 3.5 * self.scale, nostril_l[1]),
                nostril_l,
                (nostril_l[0] + 4.5 * self.scale, nostril_l[1] - 2 * self.scale),
            ], strength=0.96, width=1.55)
            engine.quality.structural_stroke([
                (nostril_r[0] + 3.5 * self.scale, nostril_r[1]),
                nostril_r,
                (nostril_r[0] - 4.5 * self.scale, nostril_r[1] - 2 * self.scale),
            ], strength=0.96, width=1.55)

            if tip:
                nose_base_pts = _catmull_rom_chain([nostril_l, (tip[0], tip[1] + 5 * self.scale), nostril_r], 5)
                engine.quality.construction_stroke(nose_base_pts, strength=0.60, width=0.90)

        # 3D nose bridge contour along dorsal crest
        bridge = data["bridge"]
        if bridge and len(bridge) >= 3:
            engine.quality.ghost_stroke(bridge, strength=0.55, width=0.85)

        # Underplane septum facet for upward pitch angles
        pose = self.analysis.get("pose", {})
        pitch = float(pose.get("pitch", 0.0) or 0.0)
        if pitch > 4.0 and tip and nostril_l and nostril_r:
            septum_pts = _catmull_rom_chain([nostril_l, (tip[0], tip[1] + 2.5 * self.scale), nostril_r], 4)
            engine.quality.structural_stroke(septum_pts, strength=0.82, width=1.15)

    def draw_lips(self, engine) -> None:
        data = self.get_lip_data()
        closure = data.get("closure")
        uo = data.get("upper_outer")
        lo = data.get("lower_outer")

        if closure:
            engine.quality.structural_stroke(closure, strength=0.98, width=1.65)
        if uo:
            engine.quality.structural_stroke(uo, strength=0.88, width=1.25)
        if lo:
            engine.quality.structural_stroke(lo, strength=0.80, width=1.15)

        for corner in [data["mouth_left"], data["mouth_right"]]:
            if corner:
                engine.quality.structural_stroke(
                    _circle_pts(corner, 1.8 * self.scale, 8), strength=0.92, width=1.0, closed=True
                )

    def draw_hair_mass_contours(self, engine, rng: Optional[random.Random] = None) -> None:
        """
        Stage 15: Hair mass, crown volume, and framing locks.
        Dynamically rendered from the uploaded photograph without hardcoded formulas.
        """
        contours = self.extractor.get_hair_contours()
        for pts in contours:
            if len(pts) >= 2:
                smooth = self.spline(pts, 3)
                engine.quality.pencil_stroke(smooth, strength=0.90, width=1.20, wobble=0.25, passes=2)

    def draw_hair_bun_and_ringlets(self, engine, rng: Optional[random.Random] = None) -> None:
        """Backwards compatibility alias for draw_hair_mass_contours."""
        self.draw_hair_mass_contours(engine, rng=rng)

    def draw_neck_and_garment(self, engine, structural_only: bool = False) -> None:
        """
        Stage 16: Neck, shoulders, and garment/dress contours.
        Dynamically extracted and rendered from the uploaded photograph.
        """
        # 1. Anatomical neck cylinder guidelines connecting jaw to clavicles
        jaw_l = self.lm(172) or self.lm(58)
        jaw_r = self.lm(397) or self.lm(288)
        chin = self.lm(CHIN)
        if jaw_l and jaw_r and chin:
            neck_w = math.hypot(jaw_r[0] - jaw_l[0], jaw_r[1] - jaw_l[1]) * 0.40
            neck_cx = (jaw_l[0] + jaw_r[0]) * 0.5
            neck_bot_y = chin[1] + neck_w * 0.90
            engine.quality.ghost_stroke([jaw_l, (neck_cx - neck_w * 0.35, neck_bot_y)], strength=0.28, width=0.75)
            engine.quality.ghost_stroke([jaw_r, (neck_cx + neck_w * 0.35, neck_bot_y)], strength=0.28, width=0.75)

        # 2. Garment / dress contours from photograph
        contours = (
            self.extractor.get_major_garment_contours()
            if structural_only
            else self.extractor.get_clothing_contours()
        )
        for pts in contours:
            if len(pts) >= 2:
                smooth = self.spline(pts, 3)
                str_val = 0.92 if structural_only else 0.88
                w_val = 1.30 if structural_only else 1.15
                engine.quality.pencil_stroke(smooth, strength=str_val, width=w_val, wobble=0.25, passes=2)

    def draw_neck_choker_and_clothing(self, engine) -> None:
        """Backwards compatibility alias for draw_neck_and_garment."""
        self.draw_neck_and_garment(engine, structural_only=False)

    def draw_cheek_forehead_contours(self, engine, strength: float = 0.5) -> None:
        """
        Stage 13: Cheek and forehead planar contours.
        Zygomatic arches, temporal ridge lines, mental protuberance (chin ball), and subtle nasolabial fold guides.
        """
        lb_tail = self.lm(70) or self.lm(46)
        rb_tail = self.lm(300) or self.lm(276)
        cheek_l = self.lm(234) or self.lm(127)
        cheek_r = self.lm(454) or self.lm(356)
        chin = self.lm(CHIN)

        # 1. Zygomatic cheekbone arch planes
        if lb_tail and cheek_l:
            engine.quality.ghost_stroke([lb_tail, cheek_l], strength=0.35 * strength, width=0.75)
        if rb_tail and cheek_r:
            engine.quality.ghost_stroke([rb_tail, cheek_r], strength=0.35 * strength, width=0.75)

        if cheek_l and chin:
            jaw_angle_l = self.lm(172) or self.lm(58)
            if jaw_angle_l:
                engine.quality.ghost_stroke([cheek_l, jaw_angle_l, chin], strength=0.30 * strength, width=0.70)
        if cheek_r and chin:
            jaw_angle_r = self.lm(397) or self.lm(288)
            if jaw_angle_r:
                engine.quality.ghost_stroke([cheek_r, jaw_angle_r, chin], strength=0.30 * strength, width=0.70)

        # 2. Temporal crest / forehead plane lines (brow up to hairline)
        hl_l = self.lm(21) or self.lm(54)
        hl_r = self.lm(251) or self.lm(284)
        if lb_tail and hl_l:
            engine.quality.ghost_stroke([lb_tail, hl_l], strength=0.30 * strength, width=0.65)
        if rb_tail and hl_r:
            engine.quality.ghost_stroke([rb_tail, hl_r], strength=0.30 * strength, width=0.65)

        # 3. Chin ball (mental protuberance)
        if chin:
            chin_r = 14.0 * self.scale
            engine.quality.ghost_stroke(
                _circle_pts((chin[0], chin[1] - chin_r * 0.7), chin_r, 20),
                strength=0.32 * strength,
                width=0.70,
                closed=True,
            )

        # 4. Subtle nasolabial fold guides
        nose_data = self.get_nose_data()
        lip_data = self.get_lip_data()
        nl = nose_data.get("nostril_l")
        nr = nose_data.get("nostril_r")
        ml = lip_data.get("mouth_left")
        mr = lip_data.get("mouth_right")
        if nl and ml:
            fold_l = _catmull_rom_chain([
                (nl[0] - 3 * self.scale, nl[1] + 2 * self.scale),
                (nl[0] - 6 * self.scale, (nl[1] + ml[1]) * 0.5),
                (ml[0] - 4 * self.scale, ml[1]),
            ], 4)
            engine.quality.ghost_stroke(fold_l, strength=0.25 * strength, width=0.60)
        if nr and mr:
            fold_r = _catmull_rom_chain([
                (nr[0] + 3 * self.scale, nr[1] + 2 * self.scale),
                (nr[0] + 6 * self.scale, (nr[1] + mr[1]) * 0.5),
                (mr[0] + 4 * self.scale, mr[1]),
            ], 4)
            engine.quality.ghost_stroke(fold_r, strength=0.25 * strength, width=0.60)

    def draw_ears_and_earrings(self, engine, strength: float = 0.90) -> None:
        """
        Stage 14: Ear construction.
        Anatomical ear placement (helix, antihelix, concha, lobule).
        Respects perspective: in 3/4 and profile views, the far ear is occluded!
        Does not fabricate synthetic jewelry.
        """
        pose = self.analysis.get("pose", {})
        yaw = float(pose.get("yaw", 0.0) or 0.0)

        l_ear = self.lm(127) or self.lm(234)
        r_ear = self.lm(356) or self.lm(454)

        ears_to_draw = []
        if yaw > 15.0:
            # 3/4 or profile looking right: only near ear (left side of head / viewer's left) is visible!
            # Far ear is on the back side of the head and occluded.
            if l_ear:
                ears_to_draw.append((l_ear, -1))
        elif yaw < -15.0:
            # 3/4 or profile looking left: only near ear (right side of head / viewer's right) is visible!
            if r_ear:
                ears_to_draw.append((r_ear, 1))
        else:
            # Frontal view: both ears if detected
            if l_ear:
                ears_to_draw.append((l_ear, -1))
            if r_ear:
                ears_to_draw.append((r_ear, 1))

        for ear_pt, sign in ears_to_draw:
            if not ear_pt:
                continue
            ear_top = (ear_pt[0] + sign * 14 * self.scale, ear_pt[1] - 22 * self.scale)
            ear_outer = (ear_pt[0] + sign * 26 * self.scale, ear_pt[1] + 2 * self.scale)
            ear_mid = (ear_pt[0] + sign * 24 * self.scale, ear_pt[1] + 22 * self.scale)
            ear_lobe = (ear_pt[0] + sign * 12 * self.scale, ear_pt[1] + 40 * self.scale)
            ear_base = (ear_pt[0] + sign * 4 * self.scale, ear_pt[1] + 34 * self.scale)

            # 1. Outer helix rim
            helix = _catmull_rom_chain([ear_pt, ear_top, ear_outer, ear_mid, ear_lobe, ear_base], 6)
            engine.quality.structural_stroke(helix, strength=0.88 * strength, width=1.30)

            # 2. Concha bowl
            concha = _catmull_rom_chain([
                (ear_top[0] - sign * 5 * self.scale, ear_top[1] + 10 * self.scale),
                (ear_outer[0] - sign * 7 * self.scale, ear_outer[1] + 5 * self.scale),
                (ear_mid[0] - sign * 8 * self.scale, ear_mid[1] + 2 * self.scale),
            ], 4)
            engine.quality.construction_stroke(concha, strength=0.65 * strength, width=0.90)

            # 3. Inner antihelix ridge
            antihelix = _catmull_rom_chain([
                (ear_top[0] - sign * 1 * self.scale, ear_top[1] + 8 * self.scale),
                (ear_outer[0] - sign * 4 * self.scale, ear_outer[1] + 10 * self.scale),
                (ear_lobe[0] - sign * 2 * self.scale, ear_lobe[1] - 5 * self.scale),
            ], 4)
            engine.quality.ghost_stroke(antihelix, strength=0.45 * strength, width=0.75)

    def draw_photo_contours(self, engine, img_path: Optional[Any] = None) -> None:
        """
        Photo-accurate contours extracted from reference portrait using bilateral filter + Canny edges.
        Captures the exact hair bun, tumbling curls, jewelry motifs, and saree drapery.
        Interior face is masked to keep facial features crisp and clean.
        """
        from pathlib import Path
        if img_path is None:
            img_path = self.img_path
        img_path = Path(img_path)
        if not img_path.exists():
            return

        img = cv2.imread(str(img_path))
        if img is None:
            return

        img_h, img_w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bi = cv2.bilateralFilter(gray, 9, 75, 75)
        edges = cv2.Canny(bi, 34, 88)

        if self.lms:
            face_mask = np.zeros((img_h, img_w), dtype=np.uint8)
            face_lm_pts = np.array([
                [int(self.lms[i]["x"]), int(self.lms[i]["y"])]
                for i in FACE_OVAL if i < len(self.lms)
            ], dtype=np.int32)
            if len(face_lm_pts) >= 6:
                cv2.fillPoly(face_mask, [face_lm_pts], 255)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (16, 16))
                face_interior = cv2.erode(face_mask, kernel)
                edges[face_interior > 0] = 0

        edges[:8, :] = 0
        edges[-8:, :] = 0
        edges[:, :8] = 0
        edges[:, -8:] = 0

        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            if cv2.arcLength(cnt, False) < 20:
                continue
            pts = cnt.squeeze(axis=1)
            if len(pts.shape) != 2 or len(pts) < 3:
                continue
            if (pts[:, 0].min() <= 8 or pts[:, 0].max() >= img_w - 9 or
                pts[:, 1].min() <= 8 or pts[:, 1].max() >= img_h - 9):
                continue
            step = max(1, len(pts) // 30)
            sampled = [self.base.transform_point((float(p[0]), float(p[1]))) for p in pts[::step]]
            if len(sampled) >= 2:
                smooth_cnt = _catmull_rom_chain(sampled, 3)
                avg_y = sum(p[1] for p in pts) / len(pts)
                if avg_y < 230:
                    engine.quality.pencil_stroke(smooth_cnt, strength=0.88, width=1.10, wobble=0.30, passes=2)
                elif 520 < avg_y < 620:
                    engine.quality.pencil_stroke(smooth_cnt, strength=0.92, width=1.20, wobble=0.25, passes=2)
                elif avg_y >= 620:
                    engine.quality.pencil_stroke(smooth_cnt, strength=0.85, width=1.15, wobble=0.30, passes=2)
                else:
                    engine.quality.pencil_stroke(smooth_cnt, strength=0.92, width=1.30, wobble=0.35, passes=2)

    def draw_shadow_structures(self, engine, rng: Optional[random.Random] = None) -> None:
        """
        Stage 18: Authentic pencil tonal shading and value planes.
        Cross-hatching under chin, eye sockets, nose, and lower lip.
        Lighting direction is estimated directly from the photograph.
        """
        if rng is None:
            rng = random.Random(1818)

        chin = self.lm(CHIN)
        light_angle = self.extractor.get_light_direction()
        if chin:
            neck_cx = chin[0]
            for i in range(16):
                y_off = chin[1] + 8 * self.scale + i * 2.2 * self.scale
                half_w = (26 - i * 1.1) * self.scale
                angle_deg = light_angle + rng.uniform(-4, 4)
                rad = math.radians(angle_deg)
                dx = half_w * math.cos(rad)
                dy = half_w * math.sin(rad)
                p0 = (neck_cx - dx, y_off - dy)
                p1 = (neck_cx + dx, y_off + dy)
                engine.quality.pencil_stroke([p0, p1], strength=0.62 - i * 0.025, width=0.85, passes=1)

        for side in ["left", "right"]:
            edata = self.get_eye_data(side)
            bdata = self.get_brow_data(side)
            if edata and bdata and edata.get("upper") and bdata.get("lower"):
                e_up = edata["upper"]
                b_lo = bdata["lower"]
                for j in range(len(e_up) - 1):
                    if j % 2 == 0 and j < len(b_lo):
                        p_bot = e_up[j]
                        p_top = b_lo[min(j, len(b_lo) - 1)]
                        engine.quality.ghost_stroke([p_bot, p_top], strength=0.22, width=0.60)

        nose_data = self.get_nose_data()
        tip = nose_data.get("tip")
        if tip:
            for k in range(5):
                sy = tip[1] + 3 * self.scale + k * 1.5 * self.scale
                sw = (8 - k * 1.2) * self.scale
                engine.quality.pencil_stroke([(tip[0] - sw, sy), (tip[0] + sw, sy)], strength=0.50 - k * 0.08, width=0.80)

        lip_data = self.get_lip_data()
        lo = lip_data.get("lower_outer")
        if lo and len(lo) >= 5:
            lo_mid = lo[len(lo) // 2]
            for m in range(6):
                ly = lo_mid[1] + 4 * self.scale + m * 1.6 * self.scale
                lw = (14 - m * 1.8) * self.scale
                engine.quality.pencil_stroke([(lo_mid[0] - lw, ly), (lo_mid[0] + lw, ly)], strength=0.55 - m * 0.07, width=0.80)

