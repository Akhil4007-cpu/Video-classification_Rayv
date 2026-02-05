def evaluate_self_harm(signals):
    """
    Detect self-harm behavior.
    Conservative, human-centered, temporal-aware.
    Enhanced with BLIP context analysis.
    """

    risk = 0.0
    reasons = []

    human = signals["human"]
    entity = signals["entity"]
    pose = signals["pose"]
    visual = signals["visual_state"]
    temporal = signals["temporal"]
    motion = signals["motion"]
    scene = signals["scene"]

    # ------------------------------------------------
    # BLIP CONTEXT ANALYSIS
    # ------------------------------------------------
    scene_labels = signals.get("scene_labels", [])
    descriptions = [label[0] if isinstance(label, tuple) else str(label) for label in scene_labels]
    self_harm_desc = " ".join(descriptions).lower()
    
    # Cooking context detection
    cooking_words = ["cooking", "food", "tomato", "vegetable", "cutting", "preparing", "kitchen", "pepper", "cutting board", "wooden"]
    is_cooking_context = any(word in self_harm_desc for word in cooking_words)
    
    # Artistic/medical context detection
    artistic_words = ["art", "painting", "sculpture", "artistic", "museum", "gallery", "classical"]
    medical_words = ["medical", "hospital", "doctor", "examination", "procedure", "surgery"]
    recreational_words = ["beach", "pool", "swimming", "bathing", "showering", "changing"]
    
    is_artistic = any(word in self_harm_desc for word in artistic_words)
    is_medical = any(word in self_harm_desc for word in medical_words)
    is_recreational = any(word in self_harm_desc for word in recreational_words)

    # ----------------------------------------
    # HARD BLOCKS (IMPORTANT - ENHANCED)
    # ----------------------------------------

    # No human → no self-harm
    if not human.get("human_present", False):
        return 0.0, []

    # Cooking / food context → NOT self-harm (ENHANCED)
    if entity.get("food_present", False) or is_cooking_context:
        return 0.0, ["Cooking/food preparation context - safe"]

    # Artistic/medical/recreational context → NOT self-harm
    if is_artistic or is_medical or is_recreational:
        return 0.0, ["Artistic/medical/recreational context - safe"]

    # Possible accident → NOT self-harm
    if temporal.get("possible_accident", False):
        return 0.0, []

    # ----------------------------------------
    # CORE SELF-HARM SIGNALS
    # ----------------------------------------

    # Blood + self-directed pose
    if (
        visual.get("blood_visible", False)
        and (
            pose.get("hands_near_chest", False)
            or pose.get("hands_near_face", False)
        )
    ):
        risk = max(risk, 0.6)
        reasons.append("Blood with self-directed hand movement")

    # Sharp object + body-focused pose (ENHANCED)
    if (
        entity.get("knife_present", False)
        and (
            pose.get("hands_near_chest", False)
            or pose.get("hands_near_face", False)
        )
        and not motion.get("aggressive_motion", False)
    ):
        # Check if it's cooking context with knife
        if not is_cooking_context:
            risk = max(risk, 0.7)
            reasons.append("Sharp object used near own body")

    # ----------------------------------------
    # TEMPORAL CONFIRMATION (VERY IMPORTANT)
    # ----------------------------------------
    if temporal.get("sustained", False) and risk > 0.5:
        risk = min(risk + 0.2, 1.0)
        reasons.append("Sustained self-harm behavior over time")

    return round(min(risk, 1.0), 3), reasons
