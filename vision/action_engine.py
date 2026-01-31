def analyze_action(signals):
    entity = signals["entity"]
    motion = signals["motion"]
    pose = signals["pose"]
    visual = signals["visual_state"]

    # ✅ COOKING
    if (
        entity.get("food_present", False)
        and pose.get("hands_detected", False)
        and not visual.get("fire_visible", False)
    ):
        return {"label": "cooking", "confidence": 0.95, "is_safe_action": True}

    # 🔥 FIRE STUNT
    if visual.get("fire_visible", False):
        return {"label": "fire_stunt", "confidence": 0.85, "is_safe_action": False}

    # 👊 FIGHT
    if motion.get("aggressive_motion", False) and pose.get("raised_arms", False):
        return {"label": "fighting", "confidence": 0.8, "is_safe_action": False}

    return {"label": "unknown", "confidence": 0.3, "is_safe_action": False}
