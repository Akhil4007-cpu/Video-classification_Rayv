import cv2
import numpy as np

def motion_risk_score(frames):
    if len(frames) < 2:
        return 0.0

    scores = []

    prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)

    for frame in frames[1:]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, prev_gray)
        score = np.mean(diff)
        scores.append(score)
        prev_gray = gray

    return float(np.mean(scores))


def fast_filter(frames,
                motion_threshold=22,
                darkness_threshold=60):
    # Handle empty frames case
    if not frames:
        return False, {
            "motion_score": 0.0,
            "dark_ratio": 0.0
        }
    
    motion_score = motion_risk_score(frames)

    dark_frames = 0
    for f in frames:
        gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        if np.mean(gray) < darkness_threshold:
            dark_frames += 1

    dark_ratio = dark_frames / len(frames)

    suspicious = (
        motion_score > motion_threshold
        or dark_ratio > 0.4
    )

    return suspicious, {
        "motion_score": motion_score,
        "dark_ratio": dark_ratio
    }
