from collections import deque


class TemporalBrain:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.memory = deque(maxlen=window_size)
        self.motion_history = []

    def add_frame_result(
        self,
        motion_score,
        risky_objects,
        safe_objects,
        clip_results
    ):
        violent_scene_score = 0.0
        safe_scene_score = 0.0

        for label, prob in clip_results:
            l = label.lower()
            if any(x in l for x in ["violent", "abuse", "attack", "fight"]):
                violent_scene_score += prob
            if any(x in l for x in ["cooking", "kitchen", "food"]):
                safe_scene_score += prob

        frame_data = {
            "motion": motion_score,
            "risky_objects": len(risky_objects),
            "safe_objects": len(safe_objects),
            "violent_scene": violent_scene_score,
            "safe_scene": safe_scene_score
        }

        self.motion_history.append(motion_score)
        self.memory.append(frame_data)

    # ---------- LEGACY INTENT (still useful) ----------
    def intent_score(self):
        if len(self.memory) < self.window_size:
            return 0.0

        motion_avg = sum(f["motion"] for f in self.memory) / self.window_size
        risky_avg = sum(f["risky_objects"] for f in self.memory) / self.window_size
        violent_scene_avg = sum(f["violent_scene"] for f in self.memory) / self.window_size
        safe_scene_avg = sum(f["safe_scene"] for f in self.memory) / self.window_size

        score = (
            0.35 * min(motion_avg / 40, 1.0) +
            0.35 * min(risky_avg / 2, 1.0) +
            0.30 * min(violent_scene_avg, 1.0)
        )

        if safe_scene_avg > violent_scene_avg:
            score *= 0.25

        return round(float(score), 3)

    # ---------- CRASH / IMPACT DETECTION ----------
    def detect_impact(self):
        if len(self.motion_history) < 3:
            return False

        avg_motion = sum(self.motion_history) / len(self.motion_history)

        for i in range(1, len(self.motion_history) - 1):
            prev_m = self.motion_history[i - 1]
            curr_m = self.motion_history[i]
            next_m = self.motion_history[i + 1]

            if (
                curr_m > avg_motion * 1.6 and
                curr_m > prev_m * 1.4 and
                curr_m > next_m * 1.4
            ):
                return True

        return False
