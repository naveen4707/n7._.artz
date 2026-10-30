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
    # CENTER AXIS
    # =========================================================

    def calculate_center_axis(self):

        forehead = self.landmark(10)

        nose_root = self.landmark(168)

        nose_tip = self.landmark(4)

        chin = self.landmark(152)

        return {

            "points": [
                forehead,
                nose_root,
                nose_tip,
                chin,
            ],

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
        }

    # =========================================================
    # CRANIUM
    # =========================================================

    def calculate_cranium(self, eyes):

        forehead = self.landmark(10)

        eye_center = eyes["center"]

        left_face = self.landmark(234)

        right_face = self.landmark(454)

        face_width = self.distance(
            left_face,
            right_face
        )

        # In Andrew Loomis 3D cranial construction, the cranial ball is a 3D sphere.
        # When viewed from 3/4 or profile angles, 2D face_width is foreshortened by cos(yaw),
        # but the 3D spherical cranial volume does not shrink.
        yaw = float(self.pose.get("yaw", 0.0) or 0.0)
        cos_yaw = max(0.55, math.cos(math.radians(abs(yaw))))
        unshortened_width = face_width / cos_yaw

        # In classical Loomis proportions, cranial sphere radius is ~0.48 of total face height
        face_height = self.distance(forehead, self.landmark(152))
        radius = max(unshortened_width / 2.0, face_height * 0.48)

        # The cranial center is positioned above the eye plane
        center = self.point(
            eye_center["x"],
            eye_center["y"] - radius * 0.52
        )

        desired_top = forehead["y"] - radius * 0.10
        current_top = center["y"] - radius
        vertical_adjustment = desired_top - current_top
        center["y"] += vertical_adjustment * 0.35

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

            "diameter": round(
                radius * 2,
                3
            ),

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
    # SIDE PLANES
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

        # Instead of arbitrary large triangles,
        # the side-plane construction is anchored
        # around the actual face boundaries.

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
        }

    # =========================================================
    # JAW CONSTRUCTION
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

        # -----------------------------------------------------
        # The actual contour is the primary jaw geometry.
        #
        # We additionally create a simplified Loomis
        # structural path using actual contour points.
        # -----------------------------------------------------

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

        # Structural jaw attachment points are selected
        # directly from the contour instead of being
        # invented with percentage-based coordinates.

        left_attachment = self.landmark(
            172
        )

        right_attachment = self.landmark(
            365
        )

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
        }

    # =========================================================
    # NOSE CONSTRUCTION
    # =========================================================

    def calculate_nose_plane(
        self,
        nose,
        eye_plane
    ):

        return {

            "root":
                nose["root"],

            "tip":
                nose["tip"],

            "leftBase":
                nose["leftBase"],

            "rightBase":
                nose["rightBase"],

            "center":
                nose["center"],

            "bridgeAxis": {

                "start":
                    nose["root"],

                "end":
                    nose["tip"],
            },

            "baseLine": {

                "start":
                    nose["leftBase"],

                "end":
                    nose["rightBase"],
            },

            "eyeToNose": {

                "start":
                    eye_plane["center"],

                "end":
                    nose["root"],
            },
        }

    # =========================================================
    # MOUTH CONSTRUCTION
    # =========================================================

    def calculate_mouth_plane(
        self,
        nose,
        mouth,
        chin
    ):

        return {

            "upperAnchor":
                nose["tip"],

            "mouthCenter":
                mouth["center"],

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
                    mouth["leftCorner"],

                "end":
                    mouth["rightCorner"],
            },
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

        center_axis = (
            self.calculate_center_axis()
        )

        cranium = (
            self.calculate_cranium(
                eyes
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
                eye_plane
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