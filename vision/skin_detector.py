import cv2
import numpy as np


def detect_skin_ratio(frame):
    """
    Returns skin exposure ratio (0.0 - 1.0)
    Enhanced with additional filters to reduce false positives.
    """

    if frame is None:
        return 0.0

    frame = cv2.resize(frame, (320, 240))

    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

    # More conservative skin detection ranges
    skin_mask = cv2.inRange(
        ycrcb,
        np.array((0, 138, 80)),   # Tightened ranges
        np.array((255, 170, 120))  # More restrictive upper bound
    )

    # Additional filtering for better accuracy
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_DILATE, kernel)

    # Filter out small skin regions (likely false positives)
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_mask = np.zeros_like(skin_mask)
    
    # Only count skin regions larger than minimum size
    min_contour_area = 500  # Increased from 0
    for contour in contours:
        if cv2.contourArea(contour) > min_contour_area:
            cv2.drawContours(filtered_mask, [contour], -1, 255, -1)
    
    skin_pixels = cv2.countNonZero(filtered_mask)
    total_pixels = filtered_mask.shape[0] * filtered_mask.shape[1]

    return round(skin_pixels / total_pixels, 3) if total_pixels else 0.0
