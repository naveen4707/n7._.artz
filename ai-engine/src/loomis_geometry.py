import math


class LoomisGeometry:
    """
    LOOMIS AI - GEOMETRY ENGINE v4

    Converts the 478 MediaPipe landmarks into:

    1. Accurate facial geometry
    2. Loomis construction geometry

    Important design principle:

        The detected face controls alignment.

        The Loomis construction simplifies the face,
        but does not invent a new jaw, eye position,
        nose position, or mouth position.
    """

    # ---------------------------------------------------------
    # IMPORTANT MEDIAPIPE LANDMARK GROUPS
    # ---------------------------------------------------------

    FACE_OVAL = [
        10,
        338,
        297,
        332,
        284,
        251,
        389,
        356,
        454,
        323,
        361,
        288,
        397,
        365,
        379,
        378,
        400,
        377,
        152,
        148,
        176,
        149,
        150,
        136,
        172,
        58,
        132,
        93,
        234,
        127,
        162,
        21,
        54,
        103,
        67,
        109,
    ]

    # Actual lower-face contour.
    JAW_CONTOUR = [
        454,
        323,
        361,
        288,
        397,
        365,
        379,
        378,
        400,
        377,
        152,
        148,
        176,
        149,
        150,
        136,
        172,
        58,
        132,
        93,
        234,
    ]

    RIGHT_EYE = [
        33,
        7,
        163,
        144,
        145,
        153,
        154,
        155,
        133,
        173,
        157,
        158,
        159,
        160,
        161,
        246,
    ]

    LEFT_EYE = [
        263,
        249,
        390,
        373,
        374,
        380,
        381,
        382,
        362,
        398,
        384,
        385,
        386,
        387,
        388,
        466,
    ]

    RIGHT_EYEBROW = [
        46,
        53,
        52,
        65,
        55,
        70,
        63,
        105,
        66,
        107,
    ]

    LEFT_EYEBROW = [
        276,
        283,
        282,
        295,
        285,
        300,
        293,
        334,
        296,
        336,
    ]

    UPPER_LIP = [
        61,
        185,
        40,
        39,
        37,
        0,
        267,
        269,
        270,
        409,
        291,
    ]

    LOWER_LIP = [
        61,
        146,
        91,
        181,
        84,
        17,
        314,
        405,
        321,
        375,
        291,
    ]

    INNER_UPPER_LIP = [
        78,
        191,
        80,
        81,
        82,
        13,
        312,
        311,
        310,
        415,
        308,
    ]

    INNER_LOWER_LIP = [
        78,
        95,
        88,
        178,
        87,
        14,
        317,
        402,
        318,
        324,
        308,
    ]

    NOSE_BRIDGE = [
        168,
        6,
        197,
        195,
        5,
        4,
    ]

    NOSE_LEFT = [
        98,
        97,
        2,
        326,
    ]

    NOSE_RIGHT = [
        326,
        327,
        294,
        278,
        344,
    ]

    NOSE_LOWER = [
        344,
        440,
        275,
        4,
        45,
        220,
        115,
        48,
        64,
        98,
    ]

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self, analysis):

        if not analysis.get("success"):
            raise ValueError(
                "Cannot create Loomis geometry from failed analysis."
            )

        self.analysis = analysis

        self.landmarks = analysis["landmarks"]

        self.pose = analysis["pose"]

        self.measurements = analysis["measurements"]

        self.width = analysis["image"]["width"]

        self.height = analysis["image"]["height"]

    # =========================================================
    # BASIC GEOMETRY
    # =========================================================

    @staticmethod
    def point(x, y, z=0.0):

        return {
            "x": round(float(x), 3),
            "y": round(float(y), 3),
            "z": round(float(z), 6),
        }

    def landmark(self, index):

        p = self.landmarks[index]

        return {
            "index": index,
            "x": round(float(p["x"]), 3),
            "y": round(float(p["y"]), 3),
            "z": round(float(p["z"]), 6),
        }

    @staticmethod
    def midpoint(a, b):

        return {
            "x": round(
                (a["x"] + b["x"]) / 2,
                3
            ),
            "y": round(
                (a["y"] + b["y"]) / 2,
                3
            ),
            "z": round(
                (
                    a.get("z", 0.0)
                    +
                    b.get("z", 0.0)
                ) / 2,
                6
            ),
        }

    @staticmethod
    def distance(a, b):

        return math.sqrt(
            (a["x"] - b["x"]) ** 2
            +
            (a["y"] - b["y"]) ** 2
        )

    @staticmethod
    def angle(a, b):

        return math.degrees(
            math.atan2(
                b["y"] - a["y"],
                b["x"] - a["x"]
            )
        )

    @staticmethod
    def interpolate(a, b, amount):

        return {
            "x": round(
                a["x"]
                +
                (b["x"] - a["x"]) * amount,
                3
            ),
            "y": round(
                a["y"]
                +
                (b["y"] - a["y"]) * amount,
                3
            ),
            "z": round(
                a.get("z", 0.0)
                +
                (
                    b.get("z", 0.0)
                    -
                    a.get("z", 0.0)
                ) * amount,
                6
            ),
        }

    def point_sequence(self, indices):

        return [
            self.landmark(index)
            for index in indices
        ]

    def group_center(self, indices):

        points = self.point_sequence(indices)

        return self.point(
            sum(p["x"] for p in points) / len(points),
            sum(p["y"] for p in points) / len(points),
            sum(p["z"] for p in points) / len(points),
        )

    # =========================================================
    # ACCURATE FACE CONTOUR
    # =========================================================

    def calculate_face_contour(self):

        all_points = self.point_sequence(
            self.FACE_OVAL
        )

        jaw_points = self.point_sequence(
            self.JAW_CONTOUR
        )

        return {
            "all": all_points,

            "jaw": jaw_points,

            "forehead": self.landmark(10),

            "rightCheek": self.landmark(454),

            "leftCheek": self.landmark(234),

            "chin": self.landmark(152),

            "landmarkIndices": self.FACE_OVAL,

            "jawLandmarkIndices": self.JAW_CONTOUR,
        }

    # =========================================================
    # EYES
    # =========================================================

    def calculate_eye(self, indices, anchor_indices):

        points = self.point_sequence(
            indices
        )

        # Use the actual anatomical eye-corner anchors for the
        # construction center. This keeps the Loomis eye plane
        # consistent with the alignment validator.
        outer_corner = self.landmark(anchor_indices[0])
        inner_corner = self.landmark(anchor_indices[1])
        center = self.midpoint(
            outer_corner,
            inner_corner
        )

        min_x = min(
            p["x"]
            for p in points
        )

        max_x = max(
            p["x"]
            for p in points
        )

        min_y = min(
            p["y"]
            for p in points
        )

        max_y = max(
            p["y"]
            for p in points
        )

        return {
            "landmarkIndices": indices,

            "points": points,

            "center": center,

            "boundingBox": {
                "left": round(min_x, 3),
                "right": round(max_x, 3),
                "top": round(min_y, 3),
                "bottom": round(max_y, 3),
                "width": round(
                    max_x - min_x,
                    3
                ),
                "height": round(
                    max_y - min_y,
                    3
                ),
            },
        }

    def calculate_eyes(self):

        # MediaPipe anatomical eye anchors:
        # Right eye: outer 33, inner 133
        # Left eye: inner 362, outer 263
        # These are the same anchors used by the alignment validator.

        right = self.calculate_eye(
            self.RIGHT_EYE,
            (33, 133)
        )

        left = self.calculate_eye(
            self.LEFT_EYE,
            (362, 263)
        )

        center = self.midpoint(
            right["center"],
            left["center"]
        )

        return {
            "right": right,
            "left": left,
            "center": center,
        }

    # =========================================================
    # EYE PLANE
    # =========================================================

    def calculate_eye_plane(self, eyes):

        start = eyes["right"]["center"]

        end = eyes["left"]["center"]

        center = self.midpoint(
            start,
            end
        )

        return {
            "start": start,

            "end": end,

            "center": center,

            "angle": round(
                self.angle(
                    start,
                    end
                ),
                3
            ),

            "width": round(
                self.distance(
                    start,
                    end
                ),
                3
            ),
        }

    # =========================================================
    # EYEBROWS
    # =========================================================

    def calculate_eyebrows(self):

        return {

            "right": {
                "indices":
                    self.RIGHT_EYEBROW,

                "points":
                    self.point_sequence(
                        self.RIGHT_EYEBROW
                    ),
            },

            "left": {
                "indices":
                    self.LEFT_EYEBROW,

                "points":
                    self.point_sequence(
                        self.LEFT_EYEBROW
                    ),
            },
        }

    # =========================================================
    # NOSE
    # =========================================================

    def calculate_nose(self):

        root = self.landmark(168)

        tip = self.landmark(4)

        center = self.landmark(1)

        left_base = self.landmark(48)

        right_base = self.landmark(278)

        return {

            "root": root,

            "bridge":
                self.point_sequence(
                    self.NOSE_BRIDGE
                ),

            "tip": tip,

            "center": center,

            "leftBase": left_base,

            "rightBase": right_base,

            "leftContour":
                self.point_sequence(
                    self.NOSE_LEFT
                ),

            "rightContour":
                self.point_sequence(
                    self.NOSE_RIGHT
                ),

            "lowerContour":
                self.point_sequence(
                    self.NOSE_LOWER
                ),

            "width": round(
                self.distance(
                    left_base,
                    right_base
                ),
                3
            ),

            "height": round(
                self.distance(
                    root,
                    tip
                ),
                3
            ),
        }

    # =========================================================
    # MOUTH
    # =========================================================

    def calculate_mouth(self):

        left = self.landmark(61)

        right = self.landmark(291)

        center = self.landmark(13)

        return {

            "upperLip":
                self.point_sequence(
                    self.UPPER_LIP
                ),

            "lowerLip":
                self.point_sequence(
                    self.LOWER_LIP
                ),

            "innerUpper":
                self.point_sequence(
                    self.INNER_UPPER_LIP
                ),

            "innerLower":
                self.point_sequence(
                    self.INNER_LOWER_LIP
                ),

            "leftCorner": left,

            "rightCorner": right,

            "center": center,

            "width": round(
                self.distance(
                    left,
                    right
                ),
                3
            ),
        }

    # =========================================================
    # CENTER AXIS & BROW EQUATOR
    # =========================================================

    def calculate_center_axis(self, cranium=None):

        forehead = self.landmark(10)
        glabella = self.landmark(9)
        nose_root = self.landmark(168)
        nose_tip = self.landmark(4)
        chin = self.landmark(152)

        # Facial midline tilt vector (chin to forehead, pointing up in 2D image coordinates)
        axis_angle_deg = self.angle(chin, forehead)
        axis_angle_rad = math.radians(axis_angle_deg)

        # Unit vector pointing UP along the facial axis
        vx_up = math.cos(axis_angle_rad)
        vy_up = math.sin(axis_angle_rad)

        # Unit vector pointing toward subject's left (camera right, perpendicular to midline)
        brow_angle_deg = axis_angle_deg + 90.0
        brow_angle_rad = math.radians(brow_angle_deg)
        ux = math.cos(brow_angle_rad)
        uy = math.sin(brow_angle_rad)

        # Unit vector pointing DOWN along the facial axis (toward chin)
        vx_down = -vx_up
        vy_down = -vy_up

        pitch = float(self.pose.get("pitch", 0.0) or 0.0)
        roll = float(self.pose.get("roll", 0.0) or 0.0)
        yaw = float(self.pose.get("yaw", 0.0) or 0.0)

        face_height = self.distance(forehead, chin)
        radius = float(cranium.get("radiusX", face_height * 0.48)) if cranium else (face_height * 0.48)

        # -----------------------------------------------------
        # 3D BROW EQUATOR (Loomis Horizontal Great Circle)
        # Passes through glabella (landmark 9) across cranial ball.
        # Bows down if pitch > 0 (looking down), bows up if pitch < 0.
        # -----------------------------------------------------
        brow_pts = []
        glab_x = glabella["x"]
        glab_y = glabella["y"]
        pitch_rad = math.radians(pitch)
        sin_pitch = math.sin(pitch_rad)

        samples = [
            -0.95, -0.80, -0.65, -0.50, -0.35, -0.18,
            0.0,
            0.18, 0.35, 0.50, 0.65, 0.80, 0.95,
        ]

        for s in samples:
            u_offset = s * (radius * 0.95)
            z_depth = math.sqrt(max(0.0, 1.0 - (s * s)))
            v_offset = (z_depth - 1.0) * sin_pitch * (radius * 0.70)
            pt_x = glab_x + (u_offset * ux) + (v_offset * vx_down)
            pt_y = glab_y + (u_offset * uy) + (v_offset * vy_down)
            brow_pts.append(self.point(pt_x, pt_y))

        brow_equator = {
            "center": glabella,
            "points": brow_pts,
            "bow": round(sin_pitch * radius * 0.70, 3),
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
            "angle": round(brow_angle_deg, 3),
        }

        meridian_points = [
            forehead,
            glabella,
            nose_root,
            nose_tip,
            self.landmark(0),
            self.landmark(13),
            self.landmark(14),
            chin,
        ]

        return {
            "points": [
                forehead,
                nose_root,
                nose_tip,
                chin,
            ],
            "meridian": meridian_points,
            "start": forehead,
            "end": chin,
            "angle": round(
                self.angle(
                    forehead,
                    chin
                ),
                3
            ),
            "noseRoot": nose_root,
            "noseTip": nose_tip,
            "glabella": glabella,
            "glabellaCross": {
                "center": glabella,
                "meridianPoint": glabella,
                "equatorPoint": glabella,
            },
            "browEquator": brow_equator,
        }

    # =========================================================
    # CRANIUM
    # =========================================================

    def calculate_cranium(self, eyes):

        forehead = self.landmark(10)
        eye_center = eyes["center"]
        left_face = self.landmark(234)
        right_face = self.landmark(454)
        chin = self.landmark(152)

        face_width = self.distance(
            left_face,
            right_face
        )

        yaw = float(self.pose.get("yaw", 0.0) or 0.0)
        pitch = float(self.pose.get("pitch", 0.0) or 0.0)
        roll = float(self.pose.get("roll", 0.0) or 0.0)

        cos_yaw = max(0.55, math.cos(math.radians(abs(yaw))))
        unshortened_width = face_width / cos_yaw

        face_height = self.distance(forehead, chin)
        radius = max(unshortened_width / 2.0, face_height * 0.48)

        center = self.point(
            eye_center["x"],
            eye_center["y"] - radius * 0.52
        )

        desired_top = forehead["y"] - radius * 0.10
        current_top = center["y"] - radius
        vertical_adjustment = desired_top - current_top
        center["y"] += vertical_adjustment * 0.35

        # -----------------------------------------------------
        # 3D CRANIAL TILT AXIS & VERTEX POLE
        # -----------------------------------------------------
        tilt_angle_deg = self.angle(chin, forehead)
        tilt_angle_rad = math.radians(tilt_angle_deg)
        ux_tilt = math.cos(tilt_angle_rad)
        uy_tilt = math.sin(tilt_angle_rad)

        top_pole = self.point(
            center["x"] + radius * ux_tilt,
            center["y"] + radius * uy_tilt
        )
        bottom_pole = self.point(
            center["x"] - radius * ux_tilt,
            center["y"] - radius * uy_tilt
        )

        tilt_axis = {
            "top": top_pole,
            "bottom": bottom_pole,
            "angle": round(tilt_angle_deg, 3),
        }

        cap_rx = radius * 0.28
        cap_ry = radius * 0.28 * max(0.20, min(0.95, abs(math.sin(math.radians(pitch + 18.0)))))
        pole_ellipse = {
            "center": top_pole,
            "radiusX": round(cap_rx, 3),
            "radiusY": round(cap_ry, 3),
            "angle": round(tilt_angle_deg + 90.0, 3),
        }

        search_radii = [
            round(radius * 0.985, 3),
            round(radius * 1.015, 3),
        ]

        return {
            "center": center,
            "radiusX": round(
                radius,
                3
            ),
            "radiusY": round(
                radius,
                3
            ),
            "radius": round(
                radius,
                3
            ),
            "diameter": round(
                radius * 2,
                3
            ),
            "tiltAxis": tilt_axis,
            "poleEllipse": pole_ellipse,
            "searchRadii": search_radii,
            "anchor": {
                "forehead":
                    forehead,
                "eyeCenter":
                    eye_center,
                "leftFace":
                    left_face,
                "rightFace":
                    right_face,
            },
        }

    # =========================================================
    # SIDE PLANES & TEMPORAL DISCS
    # =========================================================

    def calculate_side_planes(
        self,
        cranium,
        eye_plane
    ):

        center = cranium["center"]
        radius = cranium["radiusX"]
        left_face = self.landmark(234)
        right_face = self.landmark(454)

        left_upper = self.interpolate(
            center,
            left_face,
            0.72
        )

        right_upper = self.interpolate(
            center,
            right_face,
            0.72
        )

        left_inner = eye_plane["center"]
        right_inner = eye_plane["center"]

        # -----------------------------------------------------
        # ANDREW LOOMIS TEMPORAL SIDE DISCS
        # -----------------------------------------------------
        yaw = float(self.pose.get("yaw", 0.0) or 0.0)
        tilt_angle_deg = cranium.get("tiltAxis", {}).get("angle", self.angle(self.landmark(152), self.landmark(10)))
        tilt_angle_rad = math.radians(tilt_angle_deg)

        vx_up = math.cos(tilt_angle_rad)
        vy_up = math.sin(tilt_angle_rad)

        brow_angle_rad = math.radians(tilt_angle_deg + 90.0)
        hx = math.cos(brow_angle_rad)
        hy = math.sin(brow_angle_rad)

        left_disc_center = self.interpolate(center, left_face, 0.70)
        right_disc_center = self.interpolate(center, right_face, 0.70)

        r_vertical = radius * 0.58

        left_aspect = max(0.18, min(0.92, 0.28 + (0.52 * math.sin(math.radians(max(0.0, yaw + 15.0))))))
        right_aspect = max(0.18, min(0.92, 0.28 + (0.52 * math.sin(math.radians(max(0.0, -yaw + 15.0))))))

        left_rx = r_vertical * left_aspect
        left_ry = r_vertical

        right_rx = r_vertical * right_aspect
        right_ry = r_vertical

        left_v_top = self.point(left_disc_center["x"] + r_vertical * vx_up, left_disc_center["y"] + r_vertical * vy_up)
        left_v_bot = self.point(left_disc_center["x"] - r_vertical * vx_up, left_disc_center["y"] - r_vertical * vy_up)
        left_h_start = self.point(left_disc_center["x"] - left_rx * hx, left_disc_center["y"] - left_rx * hy)
        left_h_end = self.point(left_disc_center["x"] + left_rx * hx, left_disc_center["y"] + left_rx * hy)

        right_v_top = self.point(right_disc_center["x"] + r_vertical * vx_up, right_disc_center["y"] + r_vertical * vy_up)
        right_v_bot = self.point(right_disc_center["x"] - r_vertical * vx_up, right_disc_center["y"] - r_vertical * vy_up)
        right_h_start = self.point(right_disc_center["x"] - right_rx * hx, right_disc_center["y"] - right_rx * hy)
        right_h_end = self.point(right_disc_center["x"] + right_rx * hx, right_disc_center["y"] + right_rx * hy)

        temporal_discs = {
            "left": {
                "center": left_disc_center,
                "radiusX": round(left_rx, 3),
                "radiusY": round(left_ry, 3),
                "angle": round(tilt_angle_deg, 3),
                "verticalCross": {"top": left_v_top, "bottom": left_v_bot},
                "horizontalCross": {"start": left_h_start, "end": left_h_end},
                "hinge": left_v_bot,
                "visible": True,
            },
            "right": {
                "center": right_disc_center,
                "radiusX": round(right_rx, 3),
                "radiusY": round(right_ry, 3),
                "angle": round(tilt_angle_deg, 3),
                "verticalCross": {"top": right_v_top, "bottom": right_v_bot},
                "horizontalCross": {"start": right_h_start, "end": right_h_end},
                "hinge": right_v_bot,
                "visible": True,
            },
        }

        return {
            "left": {
                "upper":
                    left_upper,
                "lower":
                    left_face,
                "inner":
                    left_inner,
            },
            "right": {
                "upper":
                    right_upper,
                "lower":
                    right_face,
                "inner":
                    right_inner,
            },
            "sphereRadius":
                radius,
            "temporalDiscs":
                temporal_discs,
        }

    # =========================================================
    # JAW CONSTRUCTION & BUCKET HANDLE
    # =========================================================

    def calculate_jaw(
        self,
        face_contour,
        eye_plane
    ):

        actual = (
            face_contour["jaw"]
        )

        chin = face_contour["chin"]

        left_cheek = (
            face_contour["leftCheek"]
        )

        right_cheek = (
            face_contour["rightCheek"]
        )

        left_path = [
            self.landmark(234),
            self.landmark(93),
            self.landmark(132),
            self.landmark(58),
            self.landmark(172),
            self.landmark(136),
            self.landmark(150),
            self.landmark(149),
            self.landmark(176),
            self.landmark(148),
            self.landmark(152),
        ]

        right_path = [
            self.landmark(454),
            self.landmark(323),
            self.landmark(361),
            self.landmark(288),
            self.landmark(397),
            self.landmark(365),
            self.landmark(379),
            self.landmark(378),
            self.landmark(400),
            self.landmark(377),
            self.landmark(152),
        ]

        left_attachment = self.landmark(
            172
        )

        right_attachment = self.landmark(
            365
        )

        # -----------------------------------------------------
        # LOOMIS MANDIBLE BUCKET HANDLE & CHIN WEDGE
        # -----------------------------------------------------
        hinge_left = self.landmark(234)
        gonion_left = self.landmark(172)
        chin_left = self.landmark(148)
        chin_center = chin
        chin_right = self.landmark(377)
        gonion_right = self.landmark(365)
        hinge_right = self.landmark(454)

        chin_wedge = [
            chin_left,
            chin_center,
            chin_right,
            self.landmark(18),
        ]

        rhythm_left = [
            hinge_left,
            gonion_left,
            chin_left,
            chin_center,
        ]

        rhythm_right = [
            hinge_right,
            gonion_right,
            chin_right,
            chin_center,
        ]

        left_gonion_dist = self.distance(chin_center, gonion_left)
        right_gonion_dist = self.distance(chin_center, gonion_right)
        asymmetry_ratio = round(left_gonion_dist / max(1.0, right_gonion_dist), 3)

        bucket_handle = {
            "hingeLeft": hinge_left,
            "gonionLeft": gonion_left,
            "chinLeft": chin_left,
            "chinCenter": chin_center,
            "chinRight": chin_right,
            "gonionRight": gonion_right,
            "hingeRight": hinge_right,
            "chinWedge": chin_wedge,
            "rhythmLeft": rhythm_left,
            "rhythmRight": rhythm_right,
            "asymmetryRatio": asymmetry_ratio,
        }

        return {
            "leftAttachment":
                left_attachment,
            "rightAttachment":
                right_attachment,
            "leftCheek":
                left_cheek,
            "rightCheek":
                right_cheek,
            "chin":
                chin,
            "leftPath":
                left_path,
            "rightPath":
                right_path,
            "actualContour":
                actual,
            "eyePlaneReference":
                eye_plane["center"],
            "bucketHandle":
                bucket_handle,
        }

    # =========================================================
    # NOSE CONSTRUCTION & RULE OF THIRDS
    # =========================================================

    def calculate_nose_plane(
        self,
        nose,
        eye_plane,
        cranium=None
    ):

        root = nose["root"]
        tip = nose["tip"]
        left_base = nose["leftBase"]
        right_base = nose["rightBase"]
        center = nose["center"]

        # -----------------------------------------------------
        # RULE OF THIRDS PERSPECTIVE GUIDE LINES
        # -----------------------------------------------------
        pitch = float(self.pose.get("pitch", 0.0) or 0.0)
        face_width = self.distance(self.landmark(234), self.landmark(454))
        tilt_angle_deg = cranium.get("tiltAxis", {}).get("angle", self.angle(self.landmark(152), self.landmark(10))) if cranium else self.angle(self.landmark(152), self.landmark(10))
        tilt_angle_rad = math.radians(tilt_angle_deg)
        brow_angle_rad = math.radians(tilt_angle_deg + 90.0)

        hx = math.cos(brow_angle_rad)
        hy = math.sin(brow_angle_rad)
        vx_down = -math.cos(tilt_angle_rad)
        vy_down = -math.sin(tilt_angle_rad)

        sin_pitch = math.sin(math.radians(pitch))
        radius = float(cranium.get("radiusX", 130.0)) if cranium else 130.0

        def _make_third_arc(anchor_point):
            ax = anchor_point["x"]
            ay = anchor_point["y"]
            pts = []
            for s in (-0.85, -0.50, 0.0, 0.50, 0.85):
                u_off = s * (face_width * 0.42)
                z_depth = math.sqrt(max(0.0, 1.0 - (s * s)))
                v_off = (z_depth - 1.0) * sin_pitch * (radius * 0.50)
                pts.append(self.point(ax + u_off * hx + v_off * vx_down, ay + u_off * hy + v_off * vy_down))
            return pts

        thirds = {
            "hairline": _make_third_arc(self.landmark(10)),
            "brow": _make_third_arc(self.landmark(9)),
            "noseBase": _make_third_arc(self.landmark(2)),
            "chin": _make_third_arc(self.landmark(152)),
        }

        keystone = [
            self.landmark(107),
            self.landmark(336),
            self.landmark(6),
            self.landmark(168),
        ]

        under_plane = [
            tip,
            left_base,
            self.landmark(2),
            right_base,
        ]

        bridge_points = [
            self.landmark(168),
            self.landmark(6),
            self.landmark(197),
            self.landmark(195),
            self.landmark(5),
            tip,
        ]

        return {
            "root":
                root,
            "tip":
                tip,
            "leftBase":
                left_base,
            "rightBase":
                right_base,
            "center":
                center,
            "bridgeAxis": {
                "start":
                    root,
                "end":
                    tip,
            },
            "baseLine": {
                "start":
                    left_base,
                "end":
                    right_base,
            },
            "eyeToNose": {
                "start":
                    eye_plane["center"],
                "end":
                    root,
            },
            "thirds":
                thirds,
            "keystone":
                keystone,
            "underPlane":
                under_plane,
            "bridge":
                bridge_points,
        }

    # =========================================================
    # MOUTH CONSTRUCTION & DENTAL MUZZLE
    # =========================================================

    def calculate_mouth_plane(
        self,
        nose,
        mouth,
        chin
    ):

        left_corner = mouth["leftCorner"]
        right_corner = mouth["rightCorner"]
        mouth_center = mouth["center"]

        # -----------------------------------------------------
        # DENTAL MUZZLE (CYLINDRICAL BARREL) & NODES
        # -----------------------------------------------------
        muzzle_arc = [
            left_corner,
            self.landmark(37),
            self.landmark(0),
            self.landmark(267),
            right_corner,
        ]

        oral_fissure = [
            left_corner,
            self.landmark(78),
            self.landmark(191),
            self.landmark(80),
            self.landmark(81),
            self.landmark(13),
            self.landmark(311),
            self.landmark(310),
            self.landmark(415),
            self.landmark(308),
            right_corner,
        ]

        philtrum = [
            self.landmark(2),
            self.landmark(37),
            self.landmark(0),
            self.landmark(267),
        ]

        dental_muzzle = {
            "arc": muzzle_arc,
            "cornerNodes": {
                "left": left_corner,
                "right": right_corner,
            },
            "oralFissure": oral_fissure,
            "philtrum": philtrum,
            "labiomentalGroove": self.landmark(18),
        }

        return {
            "upperAnchor":
                nose["tip"],
            "mouthCenter":
                mouth_center,
            "chin":
                chin,
            "axis": {
                "start":
                    nose["tip"],
                "end":
                    chin,
            },
            "mouthLine": {
                "start":
                    left_corner,
                "end":
                    right_corner,
            },
            "dentalMuzzle":
                dental_muzzle,
        }

    # =========================================================
    # BUILD
    # =========================================================

    def build(self):

        face_contour = (
            self.calculate_face_contour()
        )

        eyes = (
            self.calculate_eyes()
        )

        eye_plane = (
            self.calculate_eye_plane(
                eyes
            )
        )

        eyebrows = (
            self.calculate_eyebrows()
        )

        nose = (
            self.calculate_nose()
        )

        mouth = (
            self.calculate_mouth()
        )

        cranium = (
            self.calculate_cranium(
                eyes
            )
        )

        center_axis = (
            self.calculate_center_axis(
                cranium=cranium
            )
        )

        side_planes = (
            self.calculate_side_planes(
                cranium,
                eye_plane
            )
        )

        jaw = (
            self.calculate_jaw(
                face_contour,
                eye_plane
            )
        )

        nose_plane = (
            self.calculate_nose_plane(
                nose,
                eye_plane,
                cranium=cranium
            )
        )

        mouth_plane = (
            self.calculate_mouth_plane(
                nose,
                mouth,
                face_contour["chin"]
            )
        )

        # =====================================================
        # RETURN COMPLETE GEOMETRY
        # =====================================================

        return {

            "version": "4.0",

            "engine": {

                "name":
                    "Landmark Driven Loomis Geometry",

                "landmarkCount":
                    len(self.landmarks),

                "coordinateSystem":
                    "image_pixels",

                "alignmentStrategy":
                    "landmark_anchored",
            },

            "source": {

                "poseType":
                    self.pose.get("poseType", "front"),

                "orientation":
                    self.pose.get("orientation", "front"),

                "direction":
                    self.pose.get("direction", "center"),

                "yaw":
                    self.pose.get("yaw", 0.0),

                "pitch":
                    self.pose.get("pitch", 0.0),

                "roll":
                    self.pose.get("roll", 0.0),

                "viewLabel":
                    self.pose.get("viewLabel", "Full Frontal (1/1)"),

                "viewRatio":
                    self.pose.get("viewRatio", "1/1"),

                "eyeState":
                    self.pose.get("eyeState", "Open Gaze"),

                "eyesClosed":
                    self.pose.get("eyesClosed", False),
            },

            "image": {
                "width": self.width,
                "height": self.height,
            },

            "pose": dict(self.pose),

            # -------------------------------------------------
            # ACTUAL FACE
            # -------------------------------------------------

            "accurateFace": {

                "faceContour":
                    face_contour,

                "eyes":
                    eyes,

                "eyebrows":
                    eyebrows,

                "nose":
                    nose,

                "mouth":
                    mouth,
            },

            # -------------------------------------------------
            # LOOMIS CONSTRUCTION
            # -------------------------------------------------

            "loomis": {

                "cranium":
                    cranium,

                "centerAxis":
                    center_axis,

                "eyePlane":
                    eye_plane,

                "sidePlanes":
                    side_planes,

                "jaw":
                    jaw,

                "nosePlane":
                    nose_plane,

                "mouthPlane":
                    mouth_plane,
            },

            # -------------------------------------------------
            # PROGRESSIVE STAGES
            # -------------------------------------------------

            "stages": {

                "stage01_cranium": {

                    "cranium":
                        cranium,
                },

                "stage02_axis": {

                    "cranium":
                        cranium,

                    "centerAxis":
                        center_axis,
                },

                "stage03_eye_plane": {

                    "cranium":
                        cranium,

                    "centerAxis":
                        center_axis,

                    "eyePlane":
                        eye_plane,
                },

                "stage04_jaw": {

                    "cranium":
                        cranium,

                    "centerAxis":
                        center_axis,

                    "eyePlane":
                        eye_plane,

                    "sidePlanes":
                        side_planes,

                    "jaw":
                        jaw,
                },

                "stage05_nose": {

                    "cranium":
                        cranium,

                    "centerAxis":
                        center_axis,

                    "eyePlane":
                        eye_plane,

                    "sidePlanes":
                        side_planes,

                    "jaw":
                        jaw,

                    "nosePlane":
                        nose_plane,
                },

                "stage06_mouth": {

                    "cranium":
                        cranium,

                    "centerAxis":
                        center_axis,

                    "eyePlane":
                        eye_plane,

                    "sidePlanes":
                        side_planes,

                    "jaw":
                        jaw,

                    "nosePlane":
                        nose_plane,

                    "mouthPlane":
                        mouth_plane,
                },

                "stage07_complete": {

                    "cranium":
                        cranium,

                    "centerAxis":
                        center_axis,

                    "eyePlane":
                        eye_plane,

                    "sidePlanes":
                        side_planes,

                    "jaw":
                        jaw,

                    "nosePlane":
                        nose_plane,

                    "mouthPlane":
                        mouth_plane,
                },
            },
        }