import math
from typing import Any


class FaceAnalyzer:
    """
    Converts raw facial landmarks into structured facial
    measurements that later modules can consume.
    """

    LANDMARKS = {
        "nose": 1,
        "forehead": 10,
        "chin": 152,

        "left_eye_outer": 33,
        "left_eye_inner": 133,

        "right_eye_inner": 362,
        "right_eye_outer": 263,

        "mouth_left": 61,
        "mouth_right": 291,

        "left_face": 234,
        "right_face": 454,

        "left_ear": 127,
        "right_ear": 356,
    }

    def __init__(self, landmark_analyzer, pose_estimator):
        self.landmark_analyzer = landmark_analyzer
        self.pose_estimator = pose_estimator

    @staticmethod
    def distance(point_a, point_b):
        dx = point_a["x"] - point_b["x"]
        dy = point_a["y"] - point_b["y"]

        return math.sqrt(
            (dx * dx) +
            (dy * dy)
        )

    @staticmethod
    def midpoint(point_a, point_b):
        return {
            "x": round(
                (point_a["x"] + point_b["x"]) / 2,
                3
            ),
            "y": round(
                (point_a["y"] + point_b["y"]) / 2,
                3
            ),
            "z": round(
                (point_a["z"] + point_b["z"]) / 2,
                6
            ),
        }

    @staticmethod
    def line_angle(point_a, point_b):
        angle = math.degrees(
            math.atan2(
                point_b["y"] - point_a["y"],
                point_b["x"] - point_a["x"]
            )
        )

        return round(angle, 3)

    def get_key_points(self, landmarks):
        points = {}

        for name, index in self.LANDMARKS.items():
            points[name] = landmarks[index]

        return points

    def calculate_measurements(self, points) -> dict[str, Any]:
        head_width = self.distance(
            points["left_face"],
            points["right_face"]
        )

        face_length = self.distance(
            points["forehead"],
            points["chin"]
        )

        eye_distance = self.distance(
            self.midpoint(
                points["left_eye_outer"],
                points["left_eye_inner"]
            ),
            self.midpoint(
                points["right_eye_inner"],
                points["right_eye_outer"]
            )
        )

        mouth_width = self.distance(
            points["mouth_left"],
            points["mouth_right"]
        )

        jaw_width = self.distance(
            points["left_face"],
            points["right_face"]
        )

        nose_to_chin = self.distance(
            points["nose"],
            points["chin"]
        )

        face_ratio = (
            face_length / head_width
            if head_width > 0
            else 0
        )

        return {
            "headWidth": round(head_width, 3),
            "faceLength": round(face_length, 3),
            "eyeDistance": round(eye_distance, 3),
            "mouthWidth": round(mouth_width, 3),
            "jawWidth": round(jaw_width, 3),
            "noseToChin": round(nose_to_chin, 3),
            "faceAspectRatio": round(face_ratio, 4),
        }

    def calculate_reference_lines(self, points):
        eye_left = self.midpoint(
            points["left_eye_outer"],
            points["left_eye_inner"]
        )

        eye_right = self.midpoint(
            points["right_eye_inner"],
            points["right_eye_outer"]
        )

        eye_center = self.midpoint(
            eye_left,
            eye_right
        )

        mouth_center = self.midpoint(
            points["mouth_left"],
            points["mouth_right"]
        )

        return {
            "eyeLine": {
                "start": eye_left,
                "end": eye_right,
                "center": eye_center,
                "angle": self.line_angle(
                    eye_left,
                    eye_right
                ),
            },

            "centerLine": {
                "start": points["forehead"],
                "end": points["chin"],
                "center": self.midpoint(
                    points["forehead"],
                    points["chin"]
                ),
                "angle": self.line_angle(
                    points["forehead"],
                    points["chin"]
                ),
            },

            "mouthLine": {
                "start": points["mouth_left"],
                "end": points["mouth_right"],
                "center": mouth_center,
                "angle": self.line_angle(
                    points["mouth_left"],
                    points["mouth_right"]
                ),
            },
        }

    def analyze(self, image_path):
        raw_result = self.landmark_analyzer.analyze(
            image_path
        )

        if not raw_result["detected"]:
            return {
                "success": False,
                "error": "No face detected.",
                "image": {
                    "width": raw_result["imageWidth"],
                    "height": raw_result["imageHeight"],
                },
            }

        landmarks = raw_result["landmarks"]

        pose = self.pose_estimator.estimate(
            raw_result["transformationMatrix"]
        )

        # Eye openness analysis (EAR - Eye Aspect Ratio)
        p33, p133 = landmarks[33], landmarks[133]
        p159, p145 = landmarks[159], landmarks[145]
        eye_w_l = self.distance(p33, p133)
        eye_h_l = self.distance(p159, p145)
        ear_l = eye_h_l / max(0.1, eye_w_l)

        p263, p362 = landmarks[263], landmarks[362]
        p386, p374 = landmarks[386], landmarks[374]
        eye_w_r = self.distance(p263, p362)
        eye_h_r = self.distance(p386, p374)
        ear_r = eye_h_r / max(0.1, eye_w_r)

        yaw_val = float(pose.get("yaw", 0.0) or 0.0)
        # In 3/4 or profile turns, the far eye is foreshortened which artificially inflates EAR.
        # Primary reference is the near eye (for yaw > 12: left eye / viewer's left; for yaw < -12: right eye).
        if yaw_val > 12.0:
            is_near_closed = ear_l < 0.17
        elif yaw_val < -12.0:
            is_near_closed = ear_r < 0.17
        else:
            is_near_closed = min(ear_l, ear_r) < 0.17

        if is_near_closed or (min(ear_l, ear_r) < 0.16):
            eyes_closed = True
            left_eye_open = False
            right_eye_open = False
            eye_label = "Closed Lids"
        else:
            left_eye_open = ear_l >= 0.17
            right_eye_open = ear_r >= 0.17
            eyes_closed = not left_eye_open and not right_eye_open
            eye_label = "Closed Lids" if eyes_closed else ("Partially Open" if (left_eye_open != right_eye_open) else "Open Gaze")

        eye_state = {
            "leftEar": round(ear_l, 3),
            "rightEar": round(ear_r, 3),
            "leftOpen": left_eye_open,
            "rightOpen": right_eye_open,
            "eyesClosed": eyes_closed,
            "label": eye_label,
        }
        pose["eyeState"] = eye_label
        pose["eyesClosed"] = eyes_closed

        points = self.get_key_points(
            landmarks
        )

        measurements = self.calculate_measurements(
            points
        )
        measurements["eyes"] = eye_state

        reference_lines = self.calculate_reference_lines(
            points
        )

        return {
            "success": True,

            "image": {
                "width": raw_result["imageWidth"],
                "height": raw_result["imageHeight"],
            },

            "face": {
                "detected": True,
                "landmarkCount": raw_result["landmarkCount"],
            },

            "pose": pose,

            "landmarks": landmarks,

            "keyPoints": points,

            "measurements": measurements,

            "referenceLines": reference_lines,

            "transformationMatrix": raw_result[
                "transformationMatrix"
            ],
        }

    def close(self):
        self.landmark_analyzer.close()