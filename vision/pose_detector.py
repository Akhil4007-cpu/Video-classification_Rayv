import mediapipe as mp
import cv2

class PoseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def analyze(self, frame):
        signals = {
            "human_present": False,
            "hands_detected": False,
            "hands_near_face": False,
            "hands_near_chest": False,
            "raised_arms": False
        }

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if not results.pose_landmarks:
            return signals

        lm = results.pose_landmarks.landmark
        signals["human_present"] = True
        signals["hands_detected"] = True

        left_wrist = lm[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = lm[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        nose = lm[self.mp_pose.PoseLandmark.NOSE]
        left_shoulder = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

        if left_wrist.y < nose.y or right_wrist.y < nose.y:
            signals["hands_near_face"] = True

        chest_y = (left_shoulder.y + right_shoulder.y) / 2
        if left_wrist.y < chest_y or right_wrist.y < chest_y:
            signals["hands_near_chest"] = True

        if left_wrist.y < left_shoulder.y or right_wrist.y < right_shoulder.y:
            signals["raised_arms"] = True

        return signals
