import cv2
import numpy as np


def detect_blood(frame):
    """
    Returns True if blood-like regions detected with context awareness.
    Much more conservative to avoid false positives from red food, clothing, etc.
    """

    if frame is None:
        return False

    frame = cv2.resize(frame, (320, 240))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Very specific blood-like red ranges (much narrower to avoid food false positives)
    lower_red1 = np.array([0, 150, 80])
    upper_red1 = np.array([5, 255, 180])

    lower_red2 = np.array([175, 150, 80])
    upper_red2 = np.array([180, 255, 180])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 | mask2

    # Very aggressive morphological operations to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    blood_pixels = cv2.countNonZero(mask)
    total_pixels = mask.shape[0] * mask.shape[1]

    ratio = blood_pixels / total_pixels if total_pixels else 0.0

    # Much higher threshold to avoid food false positives
    if ratio < 0.05:  # Increased from 0.03
        return False

    # Additional check: look for liquid splatter patterns (not solid food patches)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return False

    # Check if red regions have irregular, liquid-like splatter patterns
    liquid_like_count = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:  # Skip tiny noise
            continue
            
        # Check aspect ratio - food items are usually more regular
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h if h > 0 else 0
        
        # Check circularity - blood splatters are irregular, food items can be regular
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
            
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Blood splatters: low circularity, irregular aspect ratio
        # Food items: often more regular shapes
        if circularity < 0.6 and (aspect_ratio < 0.3 or aspect_ratio > 3.0):
            liquid_like_count += 1

    # Require at least 3 liquid-like red regions for blood detection
    return liquid_like_count >= 3
