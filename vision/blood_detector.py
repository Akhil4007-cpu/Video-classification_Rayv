import cv2
import numpy as np


def detect_blood(frame):
    """
    Returns True if blood-like regions detected
    Conservative thresholds to avoid false positives
    """

    if frame is None:
        return False

    frame = cv2.resize(frame, (320, 240))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # blood-like red ranges
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 | mask2

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    blood_pixels = cv2.countNonZero(mask)
    total_pixels = mask.shape[0] * mask.shape[1]

    ratio = blood_pixels / total_pixels if total_pixels else 0.0

    return ratio > 0.015
