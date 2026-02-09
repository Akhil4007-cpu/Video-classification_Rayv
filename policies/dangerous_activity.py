def evaluate_dangerous_activity(signals):
    """
    Dangerous but non-violent activities.
    Fire is handled by dedicated fire_safety policy.
    Cooking is ALWAYS safe.
    Enhanced with BLIP context analysis.
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

    # ------------------------------------------------
    # BLIP CONTEXT ANALYSIS
    # ------------------------------------------------
    scene_labels = signals.get("scene_labels", [])
    descriptions = [label[0] if isinstance(label, tuple) else str(label) for label in scene_labels]
    activity_desc = " ".join(descriptions).lower()
    
    # Cooking context detection
    cooking_words = ["cooking", "food", "tomato", "vegetable", "cutting", "preparing", "kitchen", "pepper", "cutting board", "wooden"]
    is_cooking_context = any(word in activity_desc for word in cooking_words)
    
    # Sports/recreational context detection
    sports_words = ["sport", "game", "playing", "athlete", "competition", "training", "exercise", "workout"]
    recreational_words = ["park", "playground", "recreation", "fun", "entertainment", "party"]
    
    is_sports = any(word in activity_desc for word in sports_words)
    is_recreational = any(word in activity_desc for word in recreational_words)

    if not human.get("human_present", False):
        return 0.0, []
    
    # ✅ HARD SAFE OVERRIDE — COOKING (ENHANCED)
    if (
        entity.get("food_present", False)
        and (scene.get("kitchen", False) or entity.get("knife_present", False))
        and not audio.get("panic_audio", False)
    ) or is_cooking_context:
        return 0.0, ["Safe cooking activity"]

    # ✅ SAFE OVERRIDE — SPORTS/RECREATIONAL
    if is_sports or is_recreational:
        return 0.0, ["Sports/recreational activity - safe"]

    # ✅ SAFE OVERRIDE — NORMAL ACTIVITIES (NEW)
    # Check BLIP descriptions for normal, safe activities
    normal_activity_words = [
        "sitting", "bench", "holding", "box", "table", "chair", "standing",
        "walking", "talking", "phone", "paper", "shoes", "gift", "present"
    ]
    is_normal_activity = any(word in activity_desc for word in normal_activity_words)
    
    if is_normal_activity and not entity.get("weapon_present", False):
        return 0.0, ["Normal daily activity - safe"]

    if entity.get("weapon_present", False):
        return 0.0, []

    # Note: Fire detection is now handled by fire_safety policy
    # This policy focuses on other dangerous activities

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
        # Check if it's cooking context
        if not is_cooking_context:
            risk = max(risk, 0.7)
            reasons.append("Hazardous activity near body")

    return round(min(risk, 1.0), 3), reasons
