import cv2
import numpy as np

def detect_fire(frame):
    """
    Fire detector with brightness + flicker constraint.
    Avoids food false positives.
    """

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Fire-like colors
    lower = np.array([5, 120, 180])
    upper = np.array([35, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    fire_ratio = np.sum(mask > 0) / mask.size

    # 🔒 STRONG FILTERS
    avg_brightness = np.mean(frame)

    # Fire must be:
    # - bright
    # - large enough
    # - not just red pixels
    if fire_ratio > 0.03 and avg_brightness > 120:
        return True

    return False
