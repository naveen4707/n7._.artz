import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class LandmarkAnalyzer:
    """
    Detects a face and extracts MediaPipe's 478 facial landmarks.
    """

    def __init__(
        self,
        model_path,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        base_options = python.BaseOptions(
            model_asset_path=str(model_path)
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=num_faces,
            min_face_detection_confidence=min_face_detection_confidence,
            min_face_presence_confidence=min_face_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,
        )

        self.face_landmarker = (
            vision.FaceLandmarker.create_from_options(options)
        )

    def analyze(self, image_path):
        """
        Analyze one image.

        Returns:
            {
                "detected": bool,
                "imageWidth": int,
                "imageHeight": int,
                "landmarkCount": int,
                "landmarks": [...],
                "transformationMatrix": [...]
            }
        """

        image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError(
                f"Could not read image:\n{image_path}"
            )

        height, width = image.shape[:2]

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_image
        )

        result = self.face_landmarker.detect(mp_image)

        if not result.face_landmarks:
            return {
                "detected": False,
                "imageWidth": width,
                "imageHeight": height,
                "landmarkCount": 0,
                "landmarks": [],
                "transformationMatrix": None,
            }

        face_landmarks = result.face_landmarks[0]

        landmarks = []

        for index, landmark in enumerate(face_landmarks):
            landmarks.append(
                {
                    "index": index,
                    "x": round(float(landmark.x * width), 3),
                    "y": round(float(landmark.y * height), 3),
                    "z": round(float(landmark.z), 6),
                }
            )

        transformation_matrix = None

        if result.facial_transformation_matrixes:
            matrix = result.facial_transformation_matrixes[0]

            transformation_matrix = []

            for row in matrix:
                transformation_matrix.append(
                    [
                        round(float(value), 6)
                        for value in row
                    ]
                )

        return {
            "detected": True,
            "imageWidth": width,
            "imageHeight": height,
            "landmarkCount": len(landmarks),
            "landmarks": landmarks,
            "transformationMatrix": transformation_matrix,
        }

    def close(self):
        """
        Release MediaPipe resources.
        """

        self.face_landmarker.close()