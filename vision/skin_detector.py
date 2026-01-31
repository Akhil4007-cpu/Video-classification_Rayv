import cv2
import numpy as np


def detect_skin_ratio(frame):
    """
    Returns skin exposure ratio (0.0 - 1.0)
    """

    if frame is None:
        return 0.0

    frame = cv2.resize(frame, (320, 240))

    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

    skin_mask = cv2.inRange(
        ycrcb,
        np.array((0, 133, 77)),
        np.array((255, 173, 127))
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_DILATE, kernel)

    skin_pixels = cv2.countNonZero(skin_mask)
    total_pixels = skin_mask.shape[0] * skin_mask.shape[1]

    return round(skin_pixels / total_pixels, 3) if total_pixels else 0.0
