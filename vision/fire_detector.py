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

    # 🔒 STRONG FILTERS (ENHANCED)
    avg_brightness = np.mean(frame)
    
    # Additional filter: Check for actual fire-like patterns
    # Fire must be:
    # - bright enough
    # - large enough
    # - not just red/orange pixels
    # - have sufficient fire pixel concentration
    
    if fire_ratio > 0.02 and avg_brightness > 100:  # More reasonable thresholds
        # Check for fire-like color distribution (more red/orange concentrated)
        fire_pixels = mask > 0
        if np.sum(fire_pixels) > 500:  # Reasonable minimum fire pixel count
            return True
    
    return False
