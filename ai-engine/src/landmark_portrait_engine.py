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
        pts: List[Point] = []
        for i in indices:
            p = self.lm(i)
            if p is not None:
                pts.append(p)
        return pts

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
            pt = self.base.transform_point((center["x"], center["y"]))
            if pt is not None:
                cx, cy = pt
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
        axis_pts = self.lm_pts(axis_lms)
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
        """
        Stage 11: Classical Loomis 5-plane nose construction.
        Keystone root wedge, dorsal bridge spine, lateral side slopes,
        spherical tip ball, alar wings, and columella underplane.
        """
        data = self.get_nose_data()
        tip = data["tip"]
        l_wing = data["left_wing"]
        r_wing = data["right_wing"]
        nostril_l = data["nostril_l"]
        nostril_r = data["nostril_r"]
        bridge = data.get("bridge")

        # 1. Nasal root / glabella transition
        root_pt = self.lm(168) or self.lm(6)
        if root_pt and tip:
            engine.quality.ghost_stroke([root_pt, tip], strength=0.45, width=0.80)

        # 2. Central dorsal nasal bridge spine
        if bridge and len(bridge) >= 2:
            engine.quality.structural_stroke(bridge, strength=0.82, width=1.15)

            # Lateral side slope guidelines (parallel guides along bridge)
            if len(bridge) >= 4:
                b_top = bridge[0]
                b_mid = bridge[len(bridge) // 2]
                bw = 8.0 * self.scale
                engine.quality.ghost_stroke([
                    (b_top[0] - bw * 0.7, b_top[1]),
                    (b_mid[0] - bw, b_mid[1]),
                ], strength=0.28, width=0.65)
                engine.quality.ghost_stroke([
                    (b_top[0] + bw * 0.7, b_top[1]),
                    (b_mid[0] + bw, b_mid[1]),
                ], strength=0.28, width=0.65)

        # 3. Ball of the nose (spherical tip construction)
        if tip:
            tip_r = 8.5 * self.scale
            engine.quality.construction_stroke(
                _circle_pts(tip, tip_r, 24),
                strength=0.42,
                width=0.82,
                closed=True,
            )

        # 4. Alar wings (nostril flares)
        if l_wing:
            engine.quality.structural_stroke(l_wing, strength=0.84, width=1.15)
        if r_wing:
            engine.quality.structural_stroke(r_wing, strength=0.84, width=1.15)

        # 5. Nostrils and columella under-plane
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
                engine.quality.construction_stroke(nose_base_pts, strength=0.68, width=0.95)

        # Underplane septum facet for upward pitch angles
        pose = self.analysis.get("pose", {})
        pitch = float(pose.get("pitch", 0.0) or 0.0)
        if pitch > 3.0 and tip and nostril_l and nostril_r:
            septum_pts = _catmull_rom_chain([nostril_l, (tip[0], tip[1] + 2.5 * self.scale), nostril_r], 4)
            engine.quality.structural_stroke(septum_pts, strength=0.82, width=1.15)

    def draw_lips(self, engine) -> None:
        """
        Stage 12: Classical Loomis oral architecture & dental muzzle.
        - Curved dental cylinder arc
        - Sinuous line of closure (oral fissure) with Cupid's bow dip
        - Corner modiolus nodes
        - Upper lip 3 cushions (central tubercle + 2 lateral wings)
        - Lower lip 2 cushions (left & right rounded pads with central sulcus)
        - Philtrum columns connecting subnasale to Cupid's bow
        - Labiomental groove separating lower lip from chin
        """
        data = self.get_lip_data()
        closure = data.get("closure")
        uo = data.get("upper_outer")
        lo = data.get("lower_outer")
        c_left = data.get("mouth_left")
        c_right = data.get("mouth_right")

        # 1. Cylindrical dental muzzle barrel guide
        if c_left and c_right:
            mid_x = (c_left[0] + c_right[0]) * 0.5
            mid_y = (c_left[1] + c_right[1]) * 0.5
            muzzle_w = math.hypot(c_right[0] - c_left[0], c_right[1] - c_left[1]) * 0.60
            muzzle_arc = _catmull_rom_chain([
                (c_left[0] - 6 * self.scale, c_left[1] - 4 * self.scale),
                (mid_x, mid_y - 12 * self.scale),
                (c_right[0] + 6 * self.scale, c_right[1] - 4 * self.scale),
            ], 6)
            engine.quality.ghost_stroke(muzzle_arc, strength=0.22, width=0.62)

        # 2. Sinuous line of closure (interlabial oral fissure)
        if closure:
            engine.quality.structural_stroke(closure, strength=0.98, width=1.65)

        # 3. Corner modiolus nodes (muscular nodes at oral commissures)
        for corner in [c_left, c_right]:
            if corner:
                engine.quality.structural_stroke(
                    _circle_pts(corner, 2.2 * self.scale, 8), strength=0.92, width=1.05, closed=True
                )

        # 4. Upper lip vermilion contour
        if uo:
            engine.quality.structural_stroke(uo, strength=0.88, width=1.25)

        # 5. Lower lip vermilion contour
        if lo:
            engine.quality.structural_stroke(lo, strength=0.82, width=1.18)

        # 6. Upper lip 3 cushions:
        # - Central labial tubercle (hanging down at center under Cupid's bow)
        # - Left lateral wing & Right lateral wing
        p_tubercle_top = self.lm(0)
        p_tubercle_bot = self.lm(13)
        if p_tubercle_top and p_tubercle_bot:
            tub_cx = (p_tubercle_top[0] + p_tubercle_bot[0]) * 0.5
            tub_cy = (p_tubercle_top[1] + p_tubercle_bot[1]) * 0.5
            tub_rx = 5.0 * self.scale
            tub_ry = math.hypot(p_tubercle_bot[0] - p_tubercle_top[0], p_tubercle_bot[1] - p_tubercle_top[1]) * 0.45
            tub_pts = _circle_pts((tub_cx, tub_cy), max(tub_rx, 2.5), 16)
            engine.quality.ghost_stroke(tub_pts, strength=0.32, width=0.65, closed=True)

        # 7. Lower lip 2 cushions (two side-by-side rounded oval pads):
        # Left cushion & Right cushion separated by central sulcus
        p_lo_center = self.lm(17)
        if p_lo_center and c_left and c_right:
            cushion_r = 7.5 * self.scale
            # Left cushion center
            pad_l_cx = (c_left[0] + p_lo_center[0] * 2) / 3.0
            pad_l_cy = (c_left[1] + p_lo_center[1] * 2) / 3.0 - 2 * self.scale
            engine.quality.ghost_stroke(_circle_pts((pad_l_cx, pad_l_cy), cushion_r, 16), strength=0.28, width=0.65, closed=True)

            # Right cushion center
            pad_r_cx = (c_right[0] + p_lo_center[0] * 2) / 3.0
            pad_r_cy = (c_right[1] + p_lo_center[1] * 2) / 3.0 - 2 * self.scale
            engine.quality.ghost_stroke(_circle_pts((pad_r_cx, pad_r_cy), cushion_r, 16), strength=0.28, width=0.65, closed=True)

            # Central sulcus indentation line between lower cushions
            engine.quality.ghost_stroke([
                (p_lo_center[0], p_lo_center[1] - 6 * self.scale),
                (p_lo_center[0], p_lo_center[1] + 1 * self.scale)
            ], strength=0.35, width=0.70)

        # 8. Philtrum columns connecting subnasale to Cupid's bow peaks (landmarks 37, 267)
        nose_data = self.get_nose_data()
        tip = nose_data["tip"]
        subnasale = self.lm(2) or tip
        p_cupid_l = self.lm(37)
        p_cupid_r = self.lm(267)
        if subnasale and p_cupid_l and p_cupid_r:
            engine.quality.ghost_stroke([
                (subnasale[0] - 3.5 * self.scale, subnasale[1] + 4 * self.scale),
                p_cupid_l
            ], strength=0.36, width=0.65)
            engine.quality.ghost_stroke([
                (subnasale[0] + 3.5 * self.scale, subnasale[1] + 4 * self.scale),
                p_cupid_r
            ], strength=0.36, width=0.65)

        # 9. Labiomental groove guide (separating lower lip volume from chin)
        if p_lo_center:
            groove_y = p_lo_center[1] + 9 * self.scale
            gw = 14.0 * self.scale
            engine.quality.ghost_stroke([
                (p_lo_center[0] - gw, groove_y),
                (p_lo_center[0], groove_y + 2.5 * self.scale),
                (p_lo_center[0] + gw, groove_y),
            ], strength=0.42, width=0.75)

    def draw_hair_mass_contours(self, engine, rng: Optional[random.Random] = None) -> None:
        """
        Stage 15: Volumetric hair mass, crown volume, ribbon flow, and framing locks.
        Constructs:
          - Volumetric cranial hair envelope (hair standing proud above the skull)
          - Major hair mass block boundaries (crown bun / top mass, temple masses)
          - Sinuous ribbon flow guidelines showing directional volume
          - Organic photograph silhouette contours
        """
        if rng is None:
            rng = random.Random(1515)

        # 1. Volumetric cranial envelope (hair sits 14-22px above cranium)
        cranium = self.construction.get("loomis", {}).get("cranium", {})
        center = cranium.get("center")
        if center:
            pt = self.base.transform_point((center["x"], center["y"]))
            if pt is not None:
                cx, cy = pt
                rx = float(cranium.get("radiusX", 130)) * self.scale
                ry = float(cranium.get("radiusY", 130)) * self.scale
                r_avg = (rx + ry) * 0.5
                hair_thick = 18.0 * self.scale

            # Upper crown volume arc
            crown_pts: List[Point] = []
            for deg in range(195, 346, 10):
                rad = math.radians(deg)
                px = cx + (r_avg + hair_thick) * math.cos(rad)
                py = cy + (r_avg + hair_thick * 1.15) * math.sin(rad)
                crown_pts.append((px, py))
            if len(crown_pts) >= 4:
                engine.quality.pencil_stroke(self.spline(crown_pts, 4), strength=0.88, width=1.25, passes=2)

            # 2. Volumetric ribbon flow lines (S-curves across the crown towards bun / shoulders)
            for offset_ang in [-40, -20, 0, 20, 40]:
                base_rad = math.radians(270 + offset_ang)
                p_root = (cx + r_avg * 0.95 * math.cos(base_rad), cy + r_avg * 0.95 * math.sin(base_rad))
                p_mid = (cx + (r_avg + hair_thick * 0.7) * math.cos(base_rad + 0.1), cy + (r_avg + hair_thick * 0.7) * math.sin(base_rad + 0.1))
                p_crest = (cx + (r_avg + hair_thick * 1.1) * math.cos(base_rad + 0.2), cy + (r_avg + hair_thick * 1.1) * math.sin(base_rad + 0.2))
                ribbon = _catmull_rom_chain([p_root, p_mid, p_crest], 4)
                engine.quality.ghost_stroke(ribbon, strength=0.38, width=0.75)

        # 3. Dynamic photo contours for exact hair silhouette & tumbling curls
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
        Stage 16: Classical Loomis neck and shoulder construction.
        - Cylindrical cervical column
        - Sternocleidomastoid (SCM) muscle V-rhythm from mastoids to jugular notch
        - Clavicle (collarbone) handlebar curves
        - Trapezius muscle slope down to acromion shoulder tips
        - Thyroid cartilage landmark
        - Flowing garment drape over cylindrical volumes
        """
        jaw_l = self.lm(172) or self.lm(58)
        jaw_r = self.lm(397) or self.lm(288)
        chin = self.lm(CHIN)

        if jaw_l and jaw_r and chin:
            neck_cx = (jaw_l[0] + jaw_r[0]) * 0.5
            neck_w = math.hypot(jaw_r[0] - jaw_l[0], jaw_r[1] - jaw_l[1]) * 0.44
            neck_len = neck_w * 1.05
            pit_y = chin[1] + neck_len  # Suprasternal / jugular notch

            # 1. Cylindrical cervical column guidelines
            engine.quality.ghost_stroke([jaw_l, (neck_cx - neck_w * 0.50, pit_y + 10 * self.scale)], strength=0.35, width=0.80)
            engine.quality.ghost_stroke([jaw_r, (neck_cx + neck_w * 0.50, pit_y + 10 * self.scale)], strength=0.35, width=0.80)

            # 2. Sternocleidomastoid (SCM) muscle V-rhythm (mastoids to jugular pit)
            mastoid_l = (jaw_l[0] - 8 * self.scale, jaw_l[1] - 4 * self.scale)
            mastoid_r = (jaw_r[0] + 8 * self.scale, jaw_r[1] - 4 * self.scale)
            pit_l = (neck_cx - 6 * self.scale, pit_y)
            pit_r = (neck_cx + 6 * self.scale, pit_y)

            scm_left = _catmull_rom_chain([mastoid_l, (neck_cx - neck_w * 0.28, chin[1] + neck_len * 0.5), pit_l], 5)
            scm_right = _catmull_rom_chain([mastoid_r, (neck_cx + neck_w * 0.28, chin[1] + neck_len * 0.5), pit_r], 5)

            engine.quality.construction_stroke(scm_left, strength=0.55, width=0.88)
            engine.quality.construction_stroke(scm_right, strength=0.55, width=0.88)

            # 3. Suprasternal / jugular notch (pit of the neck)
            engine.quality.ghost_stroke([
                (neck_cx - 8 * self.scale, pit_y - 2 * self.scale),
                (neck_cx, pit_y + 3 * self.scale),
                (neck_cx + 8 * self.scale, pit_y - 2 * self.scale)
            ], strength=0.45, width=0.80)

            # 4. Clavicles (collarbones) - horizontal handlebar rhythm
            clavicle_w = neck_w * 1.55
            clav_left = _catmull_rom_chain([
                pit_l,
                (neck_cx - clavicle_w * 0.5, pit_y + 2 * self.scale),
                (neck_cx - clavicle_w, pit_y + 8 * self.scale)
            ], 5)
            clav_right = _catmull_rom_chain([
                pit_r,
                (neck_cx + clavicle_w * 0.5, pit_y + 2 * self.scale),
                (neck_cx + clavicle_w, pit_y + 8 * self.scale)
            ], 5)
            engine.quality.ghost_stroke(clav_left, strength=0.40, width=0.80)
            engine.quality.ghost_stroke(clav_right, strength=0.40, width=0.80)

            # 5. Trapezius muscle slope (neck to shoulder tips)
            trap_left = _catmull_rom_chain([
                (jaw_l[0] - 12 * self.scale, jaw_l[1] + 10 * self.scale),
                (neck_cx - clavicle_w * 0.75, pit_y - 8 * self.scale),
                (neck_cx - clavicle_w * 1.25, pit_y + 22 * self.scale)
            ], 5)
            trap_right = _catmull_rom_chain([
                (jaw_r[0] + 12 * self.scale, jaw_r[1] + 10 * self.scale),
                (neck_cx + clavicle_w * 0.75, pit_y - 8 * self.scale),
                (neck_cx + clavicle_w * 1.25, pit_y + 22 * self.scale)
            ], 5)
            engine.quality.ghost_stroke(trap_left, strength=0.35, width=0.75)
            engine.quality.ghost_stroke(trap_right, strength=0.35, width=0.75)

            # 6. Thyroid cartilage landmark (centerline notch)
            larynx_y = chin[1] + neck_len * 0.38
            engine.quality.ghost_stroke([
                (neck_cx - 4 * self.scale, larynx_y),
                (neck_cx, larynx_y + 3 * self.scale),
                (neck_cx + 4 * self.scale, larynx_y)
            ], strength=0.35, width=0.65)

        # 7. Garment / dress contours from photograph
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
        Stage 13: Classical Loomis planar landmarks of the skull.
        - Zygomatic arches connecting brow tail to malar apex and angling to ear tragus
        - Temporal ridge curves ascending from brow to cranial side disc
        - Mental protuberance (chin ball & front plane wedge)
        - Nasolabial fold rhythm arcs
        """
        lb_tail = self.lm(70) or self.lm(46)
        rb_tail = self.lm(300) or self.lm(276)
        cheek_l = self.lm(234) or self.lm(127)
        cheek_r = self.lm(454) or self.lm(356)
        chin = self.lm(CHIN)

        # 1. Zygomatic cheekbone arch planes (brow tail -> malar apex -> ear tragus)
        if lb_tail and cheek_l:
            engine.quality.ghost_stroke([lb_tail, cheek_l], strength=0.40 * strength, width=0.80)
        if rb_tail and cheek_r:
            engine.quality.ghost_stroke([rb_tail, cheek_r], strength=0.40 * strength, width=0.80)

        # Malar apex to tragus / gonion angle
        jaw_angle_l = self.lm(172) or self.lm(58)
        jaw_angle_r = self.lm(397) or self.lm(288)
        if cheek_l and jaw_angle_l:
            engine.quality.ghost_stroke([cheek_l, jaw_angle_l], strength=0.32 * strength, width=0.70)
        if cheek_r and jaw_angle_r:
            engine.quality.ghost_stroke([cheek_r, jaw_angle_r], strength=0.32 * strength, width=0.70)

        # Front-to-side plane break from cheekbone to chin
        if cheek_l and chin:
            engine.quality.ghost_stroke([cheek_l, chin], strength=0.28 * strength, width=0.68)
        if cheek_r and chin:
            engine.quality.ghost_stroke([cheek_r, chin], strength=0.28 * strength, width=0.68)

        # 2. Temporal crest / frontal bone plane curves (brow tail up and back across cranium)
        hl_l = self.lm(21) or self.lm(54)
        hl_r = self.lm(251) or self.lm(284)
        if lb_tail and hl_l:
            engine.quality.ghost_stroke([lb_tail, hl_l], strength=0.35 * strength, width=0.70)
        if rb_tail and hl_r:
            engine.quality.ghost_stroke([rb_tail, hl_r], strength=0.35 * strength, width=0.70)

        # 3. Mental protuberance (chin ball / front wedge)
        if chin:
            chin_r = 13.0 * self.scale
            # Chin ball sphere
            engine.quality.ghost_stroke(
                _circle_pts((chin[0], chin[1] - chin_r * 0.65), chin_r, 20),
                strength=0.36 * strength,
                width=0.75,
                closed=True,
            )
            # Chin trapezoidal front plane wedge
            cw = 11.0 * self.scale
            engine.quality.ghost_stroke([
                (chin[0] - cw, chin[1] - chin_r * 1.1),
                (chin[0] + cw, chin[1] - chin_r * 1.1),
                (chin[0] + cw * 0.7, chin[1]),
                (chin[0] - cw * 0.7, chin[1]),
                (chin[0] - cw, chin[1] - chin_r * 1.1)
            ], strength=0.30 * strength, width=0.65)

        # 4. Nasolabial fold rhythm arcs
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
            engine.quality.ghost_stroke(fold_l, strength=0.30 * strength, width=0.65)
        if nr and mr:
            fold_r = _catmull_rom_chain([
                (nr[0] + 3 * self.scale, nr[1] + 2 * self.scale),
                (nr[0] + 6 * self.scale, (nr[1] + mr[1]) * 0.5),
                (mr[0] + 4 * self.scale, mr[1]),
            ], 4)
            engine.quality.ghost_stroke(fold_r, strength=0.30 * strength, width=0.65)

    def draw_ears_and_earrings(self, engine, strength: float = 0.90) -> None:
        """
        Stage 14: Classical Loomis ear construction.
        - Vertically bounded strictly between brow line and nose base
        - C-shaped outer helix rim
        - Inner antihelix with superior crus fork and triangular fossa
        - Concha bowl hollow
        - Tragus flap, antitragus, and lobule (earlobe)
        - Perspective awareness: far ear is occluded in 3/4 and profile poses
        """
        pose = self.analysis.get("pose", {})
        yaw = float(pose.get("yaw", 0.0) or 0.0)

        l_ear = self.lm(127) or self.lm(234)
        r_ear = self.lm(356) or self.lm(454)

        # Loomis proportion alignment levels: Brow line (top) and Nose base (bottom)
        lb = self.lm(107)
        rb = self.lm(336)
        brow_y = (lb[1] + rb[1]) * 0.5 if (lb and rb) else (l_ear[1] - 22 * self.scale if l_ear else 350.0)
        nose_base = self.lm(2)
        nose_base_y = nose_base[1] if nose_base else (l_ear[1] + 38 * self.scale if l_ear else 460.0)

        ears_to_draw = []
        if yaw > 14.0:
            # 3/4 or profile looking right: only near ear (viewer's left) is visible
            if l_ear:
                ears_to_draw.append((l_ear, -1, "left"))
        elif yaw < -14.0:
            # 3/4 or profile looking left: only near ear (viewer's right) is visible
            if r_ear:
                ears_to_draw.append((r_ear, 1, "right"))
        else:
            # Frontal view: both ears if detected
            if l_ear:
                ears_to_draw.append((l_ear, -1, "left"))
            if r_ear:
                ears_to_draw.append((r_ear, 1, "right"))

        for ear_pt, sign, side_name in ears_to_draw:
            if not ear_pt:
                continue

            # Ear vertical span: aligned with brow and nose base
            ear_top_y = brow_y
            ear_bot_y = nose_base_y
            ear_h = max(ear_bot_y - ear_top_y, 40 * self.scale)
            ear_w = ear_h * 0.32

            ear_root_x = ear_pt[0]
            ear_top = (ear_root_x + sign * ear_w * 0.45, ear_top_y)
            ear_outer = (ear_root_x + sign * ear_w, ear_top_y + ear_h * 0.32)
            ear_mid = (ear_root_x + sign * ear_w * 0.88, ear_top_y + ear_h * 0.60)
            ear_lobe = (ear_root_x + sign * ear_w * 0.45, ear_bot_y)
            ear_base = (ear_root_x + sign * ear_w * 0.15, ear_bot_y - ear_h * 0.12)

            # Loomis alignment construction guide ticks (connecting cheek/cranium margin to ear top & bottom)
            engine.quality.ghost_stroke([
                (ear_root_x - sign * 12 * self.scale, ear_top_y),
                (ear_top[0] + sign * 2 * self.scale, ear_top_y)
            ], strength=0.20 * strength, width=0.55)
            engine.quality.ghost_stroke([
                (ear_root_x - sign * 12 * self.scale, ear_bot_y),
                (ear_lobe[0] + sign * 2 * self.scale, ear_bot_y)
            ], strength=0.20 * strength, width=0.55)

            # 1. Outer C-shaped helix rim
            helix = _catmull_rom_chain([ear_pt, ear_top, ear_outer, ear_mid, ear_lobe, ear_base], 6)
            engine.quality.structural_stroke(helix, strength=0.88 * strength, width=1.30)

            # 2. Inner antihelix ridge with superior crus fork
            antihelix_main = _catmull_rom_chain([
                (ear_outer[0] - sign * ear_w * 0.22, ear_top_y + ear_h * 0.30),
                (ear_mid[0] - sign * ear_w * 0.25, ear_top_y + ear_h * 0.55),
                (ear_lobe[0] - sign * ear_w * 0.10, ear_bot_y - ear_h * 0.18),
            ], 4)
            engine.quality.construction_stroke(antihelix_main, strength=0.62 * strength, width=0.88)

            # Superior crus (fork pointing toward top apex)
            crus_pts = [
                (ear_outer[0] - sign * ear_w * 0.22, ear_top_y + ear_h * 0.30),
                (ear_top[0] - sign * ear_w * 0.15, ear_top_y + ear_h * 0.15)
            ]
            engine.quality.ghost_stroke(crus_pts, strength=0.40 * strength, width=0.70)

            # 3. Concha bowl hollow
            concha = _catmull_rom_chain([
                (ear_root_x + sign * ear_w * 0.20, ear_top_y + ear_h * 0.38),
                (ear_root_x + sign * ear_w * 0.52, ear_top_y + ear_h * 0.45),
                (ear_root_x + sign * ear_w * 0.32, ear_top_y + ear_h * 0.65),
            ], 4)
            engine.quality.structural_stroke(concha, strength=0.72 * strength, width=1.0)

            # 4. Tragus flap (protective nodule over ear canal)
            tragus_pts = [
                (ear_root_x, ear_top_y + ear_h * 0.42),
                (ear_root_x + sign * ear_w * 0.22, ear_top_y + ear_h * 0.48),
                (ear_root_x + sign * ear_w * 0.08, ear_top_y + ear_h * 0.55),
            ]
            engine.quality.structural_stroke(tragus_pts, strength=0.78 * strength, width=1.05)

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
            raw_sampled = [self.base.transform_point((float(p[0]), float(p[1]))) for p in pts[::step]]
            sampled: List[Point] = [p for p in raw_sampled if p is not None]
            if len(sampled) >= 2:
                smooth_cnt = _catmull_rom_chain(sampled, 3)
                avg_y = sum(p[1] for p in pts) / len(pts)
                rel_y = avg_y / max(1.0, float(img_h))
                if rel_y < 0.28:
                    engine.quality.pencil_stroke(smooth_cnt, strength=0.88, width=1.10, wobble=0.30, passes=2)
                elif 0.60 < rel_y < 0.72:
                    engine.quality.pencil_stroke(smooth_cnt, strength=0.92, width=1.20, wobble=0.25, passes=2)
                elif rel_y >= 0.72:
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

        light_angle = self.extractor.get_light_direction()

        # 1. UNDER-JAW & NECK CYLINDER CAST SHADOW
        chin = self.lm(CHIN)
        jaw_l = self.lm(172) or self.lm(58)
        jaw_r = self.lm(397) or self.lm(288)
        if chin:
            neck_cx = chin[0] if not (jaw_l and jaw_r) else (jaw_l[0] + jaw_r[0]) * 0.5
            neck_w = math.hypot(jaw_r[0] - jaw_l[0], jaw_r[1] - jaw_l[1]) * 0.44 if (jaw_l and jaw_r) else 65.0 * self.scale

            # Primary hatch pass: parallel to estimated light angle
            for i in range(20):
                y_off = chin[1] + 6 * self.scale + i * 2.2 * self.scale
                half_w = (neck_w * 0.50) * max(0.2, 1.0 - i * 0.028)
                angle_deg = light_angle + rng.uniform(-3, 3)
                rad = math.radians(angle_deg)
                dx = half_w * math.cos(rad)
                dy = half_w * math.sin(rad)
                p0 = (neck_cx - dx, y_off - dy)
                p1 = (neck_cx + dx, y_off + dy)
                str_val = max(0.18, 0.68 - i * 0.025)
                engine.quality.pencil_stroke([p0, p1], strength=str_val, width=0.85, passes=1)

            # Secondary cross-hatch pass: -42 degrees to light angle (densest near jaw rim)
            for i in range(12):
                y_off = chin[1] + 6 * self.scale + i * 2.4 * self.scale
                half_w = (neck_w * 0.42) * max(0.2, 1.0 - i * 0.035)
                angle_deg = light_angle - 42.0 + rng.uniform(-3, 3)
                rad = math.radians(angle_deg)
                dx = half_w * math.cos(rad)
                dy = half_w * math.sin(rad)
                p0 = (neck_cx - dx, y_off - dy)
                p1 = (neck_cx + dx, y_off + dy)
                str_val = max(0.16, 0.52 - i * 0.030)
                engine.quality.pencil_stroke([p0, p1], strength=str_val, width=0.80, passes=1)

        # 2. ORBITAL EYE SOCKET HOLLOWS & MEDIAL CANTHUS RECESSES
        for side in ["left", "right"]:
            edata = self.get_eye_data(side)
            bdata = self.get_brow_data(side)
            if edata and bdata:
                e_up = edata.get("upper") or edata.get("upper_lid", [])
                b_lo = bdata.get("lower", [])
                if e_up and b_lo:
                    for j in range(len(e_up) - 1):
                        if j % 2 == 0 and j < len(b_lo):
                            p_bot = e_up[j]
                            p_top = b_lo[min(j, len(b_lo) - 1)]
                            mid_x = (p_bot[0] + p_top[0]) * 0.5
                            mid_y = (p_bot[1] + p_top[1]) * 0.5
                            hx = 3.0 * self.scale
                            hy = 4.5 * self.scale
                            engine.quality.ghost_stroke([(mid_x - hx, mid_y - hy), (mid_x + hx, mid_y + hy)], strength=0.28, width=0.65)

                inner = edata.get("inner")
                if inner:
                    sign = -1 if side == "left" else 1
                    for s_idx in range(4):
                        hx = inner[0] + sign * (2.2 + s_idx * 1.8) * self.scale
                        hy = inner[1] - (1.5 + s_idx * 2.2) * self.scale
                        engine.quality.ghost_stroke([
                            (hx - 2.5 * self.scale, hy - 2.0 * self.scale),
                            (hx + 2.5 * self.scale, hy + 2.0 * self.scale)
                        ], strength=0.34 - s_idx * 0.05, width=0.70)

        # 3. NOSE PLANES: SUBNASALE CAST SHADOW & LATERAL SLOPE
        nose_data = self.get_nose_data()
        tip = nose_data.get("tip")
        subnasale = self.lm(2)
        if tip:
            ref_pt = subnasale if subnasale else tip
            # Primary drop shadow beneath columella
            for k in range(6):
                sy = ref_pt[1] + 2.5 * self.scale + k * 1.5 * self.scale
                sw = (10.0 - k * 1.4) * self.scale
                ang = 18.0 + rng.uniform(-3, 3)
                dx = sw * math.cos(math.radians(ang))
                dy = sw * math.sin(math.radians(ang))
                engine.quality.pencil_stroke([(ref_pt[0] - dx, sy - dy), (ref_pt[0] + dx, sy + dy)], strength=0.60 - k * 0.08, width=0.82)
            # Cross-hatch under nose
            for k in range(3):
                sy = ref_pt[1] + 3.0 * self.scale + k * 1.6 * self.scale
                sw = (7.5 - k * 1.6) * self.scale
                ang = -28.0 + rng.uniform(-3, 3)
                dx = sw * math.cos(math.radians(ang))
                dy = sw * math.sin(math.radians(ang))
                engine.quality.pencil_stroke([(ref_pt[0] - dx, sy - dy), (ref_pt[0] + dx, sy + dy)], strength=0.48 - k * 0.09, width=0.75)

            # Shadow on lateral slope of the bridge
            bridge_pts = self.lm_pts(NOSE_BRIDGE)
            shadow_sign = 1 if math.cos(math.radians(light_angle)) >= 0 else -1
            if len(bridge_pts) >= 3:
                for bp in bridge_pts[1:-1]:
                    hx = bp[0] + shadow_sign * 5.0 * self.scale
                    hy = bp[1]
                    engine.quality.ghost_stroke([
                        (hx, hy - 3.0 * self.scale),
                        (hx + shadow_sign * 3.0 * self.scale, hy + 3.0 * self.scale)
                    ], strength=0.30, width=0.65)

        # 4. LIPS & MOUTH TONAL PLANES
        lip_data = self.get_lip_data()
        # Upper lip downward planar shading
        uo = lip_data.get("upper_outer", [])
        ui = lip_data.get("upper_inner", [])
        if uo and ui and len(uo) >= 5 and len(ui) >= 5:
            for idx in range(1, len(uo) - 1, 2):
                p_top = uo[idx]
                p_bot = ui[min(idx, len(ui) - 1)]
                engine.quality.pencil_stroke([p_top, p_bot], strength=0.52, width=0.80, passes=1)

        # Sub-labial / Labiomental groove crescent shadow below lower lip
        lo = lip_data.get("lower_outer", [])
        if lo and len(lo) >= 5:
            lo_mid = lo[len(lo) // 2]
            # Primary pass
            for m in range(7):
                ly = lo_mid[1] + 3.5 * self.scale + m * 1.5 * self.scale
                lw = (15.0 - m * 1.8) * self.scale
                engine.quality.pencil_stroke([(lo_mid[0] - lw, ly), (lo_mid[0] + lw, ly)], strength=0.58 - m * 0.07, width=0.82)
            # Cross-hatch pass
            for m in range(4):
                ly = lo_mid[1] + 4.0 * self.scale + m * 1.8 * self.scale
                lw = (11.0 - m * 2.0) * self.scale
                dx = lw * 0.88
                dy = lw * 0.28
                engine.quality.pencil_stroke([(lo_mid[0] - dx, ly - dy), (lo_mid[0] + dx, ly + dy)], strength=0.44 - m * 0.08, width=0.75)

        # Modiolus corner accents
        c_left = lip_data.get("left")
        c_right = lip_data.get("right")
        if c_left:
            engine.quality.pencil_stroke([(c_left[0] - 2.5 * self.scale, c_left[1]), (c_left[0] + 2.5 * self.scale, c_left[1])], strength=0.72, width=1.10)
        if c_right:
            engine.quality.pencil_stroke([(c_right[0] - 2.5 * self.scale, c_right[1]), (c_right[0] + 2.5 * self.scale, c_right[1])], strength=0.72, width=1.10)

        # 5. CHIN BALL MENTAL PROTUBERANCE UNDERSIDE
        if chin:
            for ci in range(4):
                c_rad = (11.0 - ci * 1.8) * self.scale
                cy = chin[1] - 3.5 * self.scale + ci * 1.5 * self.scale
                engine.quality.pencil_stroke([(chin[0] - c_rad, cy), (chin[0] + c_rad, cy)], strength=0.42 - ci * 0.08, width=0.78)

        # 6. ZYGOMATIC CHEEK HOLLOWS (BUCCAL DEPRESSIONS)
        malar_l = self.lm(116)
        malar_r = self.lm(345)
        for malar, sign in [(malar_l, -1), (malar_r, 1)]:
            if malar:
                for ch_i in range(5):
                    cx0 = malar[0] + sign * (4.0 + ch_i * 2.2) * self.scale
                    cy0 = malar[1] + (8.0 + ch_i * 3.2) * self.scale
                    dx = 7.0 * self.scale * sign
                    dy = 10.0 * self.scale
                    engine.quality.ghost_stroke([(cx0, cy0), (cx0 + dx, cy0 + dy)], strength=0.26 - ch_i * 0.03, width=0.65)

    def draw_hair_tonal_volume(self, engine, rng: Optional[random.Random] = None) -> None:
        """
        Renders rich procedural hand-drawn graphite tonal modeling across the hair mass.
        Builds deep 4B/6B graphite tone, directional hair flow, and fiber luster
        without any raster photo overlay.
        """
        if rng is None:
            rng = random.Random(2024)

        cranium = self.construction.get("loomis", {}).get("cranium", {})
        center = cranium.get("center")
        if center:
            pt = self.base.transform_point((center["x"], center["y"]))
            if pt is not None:
                cx, cy = pt
                rx = float(cranium.get("radiusX", 130)) * self.scale
                ry = float(cranium.get("radiusY", 130)) * self.scale
                r_avg = (rx + ry) * 0.5
                hair_thick = 20.0 * self.scale

            # 1. Multi-pass directional crown sweeps from forehead part down towards temples and back
            for ang_deg in range(190, 351, 6):
                base_rad = math.radians(ang_deg)
                p0 = (cx + (r_avg * 0.88 + rng.uniform(-3, 3) * self.scale) * math.cos(base_rad),
                      cy + (r_avg * 0.88 + rng.uniform(-3, 3) * self.scale) * math.sin(base_rad))
                p1 = (cx + (r_avg + hair_thick * 0.6 + rng.uniform(-2, 2) * self.scale) * math.cos(base_rad + 0.08),
                      cy + (r_avg + hair_thick * 0.6 + rng.uniform(-2, 2) * self.scale) * math.sin(base_rad + 0.08))
                p2 = (cx + (r_avg + hair_thick * 1.05) * math.cos(base_rad + 0.15),
                      cy + (r_avg + hair_thick * 1.05) * math.sin(base_rad + 0.15))
                sweep = _catmull_rom_chain([p0, p1, p2], 4)
                engine.quality.pencil_stroke(sweep, strength=0.72 + rng.uniform(-0.1, 0.15), width=1.10, wobble=0.25, passes=2)

            # 2. Deep core shading in the back crown / bun mass
            bun_cx = cx + rx * 0.45
            bun_cy = cy - ry * 0.55
            for b_i in range(16):
                b_ang = math.radians(b_i * 22.5)
                b_r = (22.0 + (b_i % 4) * 6.0) * self.scale
                p_start = (bun_cx + b_r * 0.4 * math.cos(b_ang), bun_cy + b_r * 0.4 * math.sin(b_ang))
                p_end = (bun_cx + b_r * math.cos(b_ang + 0.5), bun_cy + b_r * math.sin(b_ang + 0.5))
                engine.quality.pencil_stroke([p_start, p_end], strength=0.82, width=1.15, passes=2)

        # 3. Dynamic hair contours from photo with multi-pass graphite depth
        hair_contours = self.extractor.get_hair_contours()
        for idx, pts in enumerate(hair_contours):
            if len(pts) >= 3:
                smooth = self.spline(pts, 3)
                engine.quality.pencil_stroke(smooth, strength=0.92, width=1.35, wobble=0.25, passes=2)
                if len(smooth) >= 4 and idx % 2 == 0:
                    offset_pts = [(p[0] + rng.uniform(-1.5, 1.5) * self.scale, p[1] + 2.0 * self.scale) for p in smooth]
                    engine.quality.pencil_stroke(offset_pts, strength=0.68, width=0.95, wobble=0.30, passes=1)

    def draw_luminous_highlights(self, image: Image.Image) -> None:
        """
        Adds soft eraser-lift luminous highlights to key anatomical focal points:
          - Pure white specular catchlights in eye pupils
          - Apex highlight on nose tip ball
          - Central highlight on lower lip cushion
          - Subtle highlight ridge along dorsal nasal bridge
        """
        draw = ImageDraw.Draw(image)
        # 1. Specular pupil catchlights
        for side in ["left", "right"]:
            edata = self.get_eye_data(side)
            if edata and not edata.get("is_closed", False):
                ic = edata.get("iris_center")
                ir = edata.get("iris_r", 12.0)
                if ic:
                    _draw_white_dot(image, ic[0] - ir * 0.28, ic[1] - ir * 0.32, max(ir * 0.18, 2.5))

        # 2. Nose tip highlight (eraser lift)
        nose_data = self.get_nose_data()
        tip = nose_data.get("tip")
        if tip:
            _draw_white_dot(image, tip[0] - 1.5 * self.scale, tip[1] - 1.5 * self.scale, 2.8 * self.scale)
            bridge = nose_data.get("bridge")
            if bridge and len(bridge) >= 3:
                mid_b = bridge[len(bridge) // 2]
                draw.line(
                    [(mid_b[0] - 0.5 * self.scale, mid_b[1]), (mid_b[0] - 0.5 * self.scale, mid_b[1] + 8.0 * self.scale)],
                    fill=(255, 255, 255),
                    width=int(max(1, 1.5 * self.scale))
                )

        # 3. Lower lip central highlight cushion
        lip_data = self.get_lip_data()
        lo = lip_data.get("lower_outer")
        li = lip_data.get("lower_inner")
        if lo and li and len(lo) >= 5 and len(li) >= 5:
            mid_lo = lo[len(lo) // 2]
            mid_li = li[len(li) // 2]
            lip_c_y = (mid_lo[1] + mid_li[1]) * 0.5
            lip_c_x = (mid_lo[0] + mid_li[0]) * 0.5
            hl_w = 6.0 * self.scale
            draw.line(
                [(lip_c_x - hl_w, lip_c_y), (lip_c_x + hl_w, lip_c_y)],
                fill=(255, 255, 255),
                width=int(max(1, 1.8 * self.scale))
            )


