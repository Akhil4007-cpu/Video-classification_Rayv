def evaluate_dangerous_activity(signals):
    """
    Dangerous but non-violent activities.
    Cooking is ALWAYS safe.
    """

    risk = 0.0
    reasons = []

    human = signals["human"]
    motion = signals["motion"]
    visual = signals["visual_state"]
    pose = signals["pose"]
    audio = signals["audio"]
    scene = signals["scene"]
    entity = signals["entity"]

    if not human.get("human_present", False):
        return 0.0, []
    
     

    # ✅ HARD SAFE OVERRIDE — COOKING
    if (
        entity.get("food_present", False)
        and (scene.get("kitchen", False) or entity.get("knife_present", False))
        and not audio.get("panic_audio", False)
    ):
        return 0.0, ["Safe cooking activity"]

    if entity.get("weapon_present", False):
        return 0.0, []

    if visual.get("fire_visible", False):
        risk = max(risk, 0.85)
        reasons.append("Fire or flame detected near human")

    if (
        motion.get("motion_score", 0) > 40
        and motion.get("aggressive_motion", False)
        and not audio.get("panic_audio", False)
    ):
        risk = max(risk, 0.6)
        reasons.append("High-risk physical activity detected")

    if (
        (pose.get("hands_near_face", False) or pose.get("hands_near_chest", False))
        and motion.get("motion_score", 0) > 35
    ):
        risk = max(risk, 0.7)
        reasons.append("Hazardous activity near body")

    return round(min(risk, 1.0), 3), reasons
