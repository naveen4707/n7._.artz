import math


class PoseEstimator:
    """
    Estimates head orientation from MediaPipe's
    4x4 facial transformation matrix.
    """

    def estimate(self, transformation_matrix):
        if not transformation_matrix:
            return {
                "available": False,
                "yaw": None,
                "pitch": None,
                "roll": None,
                "orientation": "unknown",
                "direction": "unknown",
                "poseType": "unknown",
                "confidence": 0.0,
            }

        if len(transformation_matrix) < 3:
            return {
                "available": False,
                "yaw": None,
                "pitch": None,
                "roll": None,
                "orientation": "unknown",
                "direction": "unknown",
                "poseType": "unknown",
                "confidence": 0.0,
            }

        r00 = transformation_matrix[0][0]
        r01 = transformation_matrix[0][1]
        r02 = transformation_matrix[0][2]

        r10 = transformation_matrix[1][0]
        r11 = transformation_matrix[1][1]
        r12 = transformation_matrix[1][2]

        r20 = transformation_matrix[2][0]
        r21 = transformation_matrix[2][1]
        r22 = transformation_matrix[2][2]

        # -------------------------------------------------
        # Convert rotation matrix to Euler angles
        # -------------------------------------------------

        yaw = math.atan2(
            -r20,
            math.sqrt(
                (r00 * r00) +
                (r10 * r10)
            )
        )

        pitch = math.atan2(
            r21,
            r22
        )

        roll = math.atan2(
            r10,
            r00
        )

        yaw_deg = math.degrees(yaw)
        pitch_deg = math.degrees(pitch)
        roll_deg = math.degrees(roll)

        # -------------------------------------------------
        # Classify horizontal orientation (Loomis Views)
        # -------------------------------------------------

        abs_yaw = abs(yaw_deg)

        if abs_yaw < 12:
            orientation = "front"
            pose_type = "front"
            view_label = "Full Frontal (1/1)"
            view_ratio = "1/1"

        elif abs_yaw < 25:
            orientation = "quarter"
            turn = "Right" if yaw_deg > 0 else "Left"
            pose_type = f"quarter_{turn.lower()}"
            view_label = f"Quarter View ({turn} 1/4)"
            view_ratio = "1/4"

        elif abs_yaw < 55:
            orientation = "three_quarter"
            turn = "Right" if yaw_deg > 0 else "Left"
            pose_type = f"three_quarter_{turn.lower()}"
            view_label = f"3/4 View ({turn})"
            view_ratio = "3/4"

        else:
            orientation = "profile"
            turn = "Right" if yaw_deg > 0 else "Left"
            pose_type = f"profile_{turn.lower()}"
            view_label = f"Profile / Half ({turn} 1/2)"
            view_ratio = "1/2"

        # -------------------------------------------------
        # Classify vertical tilt (Pitch)
        # -------------------------------------------------
        if pitch_deg > 6:
            tilt_label = f"Looking Up (+{pitch_deg:.1f}°)"
            tilt_type = "up"
        elif pitch_deg < -6:
            tilt_label = f"Looking Down ({pitch_deg:.1f}°)"
            tilt_type = "down"
        else:
            tilt_label = "Level Gaze"
            tilt_type = "level"

        # -------------------------------------------------
        # Direction
        # -------------------------------------------------

        if yaw_deg > 8:
            direction = "right"
        elif yaw_deg < -8:
            direction = "left"
        else:
            direction = "center"

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        rotation_penalty = min(abs_yaw / 90.0, 1.0)
        confidence = 1.0 - (rotation_penalty * 0.4)
        confidence = max(0.0, min(1.0, confidence))

        return {
            "available": True,
            "yaw": round(yaw_deg, 3),
            "pitch": round(pitch_deg, 3),
            "roll": round(roll_deg, 3),
            "orientation": orientation,
            "direction": direction,
            "poseType": pose_type,
            "viewLabel": view_label,
            "viewRatio": view_ratio,
            "tiltLabel": tilt_label,
            "tiltType": tilt_type,
            "confidence": round(confidence, 3),
        }