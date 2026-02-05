def evaluate_nudity(signals):
    """
    Enhanced nudity detection with BLIP context analysis.
    Requires sexualized context, not just skin exposure.

    Enhanced with BLIP descriptions to distinguish:
    - Sexualized content vs artistic/medical/recreational
    - Beach/pool contexts vs private contexts
    - Educational content vs explicit content
    """

    risk = 0.0
    reasons = []

    human = signals.get("human", {})
    visual = signals.get("visual_state", {})
    scene = signals.get("scene", {})
    pose = signals.get("pose", {})
    motion = signals.get("motion", {})

    # ------------------------------------------------
    # BLIP NUDITY CONTEXT ANALYSIS
    # ------------------------------------------------
    scene_labels = signals.get("scene_labels", [])
    descriptions = [label[0] if isinstance(label, tuple) else str(label) for label in scene_labels]
    nudity_desc = " ".join(descriptions).lower()
    
    # Context detection
    sexualized_words = ["sexual", "erotic", "intimate", "seductive", "provocative", "explicit", "nude", "naked"]
    artistic_words = ["art", "painting", "sculpture", "artistic", "museum", "gallery", "classical"]
    medical_words = ["medical", "hospital", "doctor", "examination", "procedure", "surgery"]
    recreational_words = ["beach", "pool", "swimming", "bathing", "showering", "changing", "bathing suit"]
    private_words = ["bedroom", "private", "home", "alone", "intimate"]

    is_sexualized = any(word in nudity_desc for word in sexualized_words)
    is_artistic = any(word in nudity_desc for word in artistic_words)
    is_medical = any(word in nudity_desc for word in medical_words)
    is_recreational = any(word in nudity_desc for word in recreational_words)
    is_private = any(word in nudity_desc for word in private_words)

    skin = visual.get("skin_exposure_ratio", 0.0)

    # ------------------------------------------------
    # HARD BLOCK — NO HUMAN
    # ------------------------------------------------
    if not human.get("human_present", False):
        return 0.0, []

    # ------------------------------------------------
    # HARD BLOCK — FIRE / HAZARDOUS ACTIVITY
    # ------------------------------------------------
    if (
        motion.get("aggressive_motion", False)
        and motion.get("motion_score", 0) > 40
    ):
        return 0.0, []

    # ------------------------------------------------
    # 🔴 CHILD SAFETY (ZERO TOLERANCE)
    # ------------------------------------------------
    if human.get("child_present", False) and skin > 0.1:
        return 1.0, ["Child nudity risk"]

    # ------------------------------------------------
    # CLEAR SAFE — LOW SKIN
    # ------------------------------------------------
    if skin < 0.15:
        return 0.0, []

    # ------------------------------------------------
    # ENHANCED CONTEXT-BASED ASSESSMENT
    # ------------------------------------------------
    if is_sexualized:
        if "explicit" in nudity_desc or "naked" in nudity_desc:
            risk = max(risk, 0.95)
            reasons.append("Explicit sexual content detected")
        else:
            risk = max(risk, 0.8)
            reasons.append("Sexualized content detected")
    
    elif is_medical:
        risk = max(risk, 0.2)
        reasons.append("Medical/educational context")
    
    elif is_artistic:
        risk = max(risk, 0.3)
        reasons.append("Artistic nudity detected")
    
    elif is_recreational:
        risk = max(risk, 0.4)
        reasons.append("Recreational nudity (beach/pool)")
    
    elif is_private and skin > 0.5:
        risk = max(risk, 0.7)
        reasons.append("High skin exposure in private context")

    # ------------------------------------------------
    # OUTDOOR / PUBLIC CONTEXT (NON-SEXUAL)
    # ------------------------------------------------
    if scene.get("outdoor", False) and skin < 0.5 and not is_sexualized:
        return 0.0, []

    # ------------------------------------------------
    # SEXUALIZED NUDITY (ENHANCED CORE LOGIC)
    # ------------------------------------------------
    if (
        skin > 0.35
        and (
            pose.get("hands_near_chest", False)
            or pose.get("hands_near_face", False)
        )
        and not motion.get("aggressive_motion", False)
    ):
        if is_sexualized:
            risk = max(risk, 0.9)
            reasons.append("Sexualized pose with explicit context")
        else:
            risk = max(risk, 0.75)
            reasons.append("Sexualized pose with skin exposure")

    # ------------------------------------------------
    # VERY HIGH SKIN + INDOOR (ENHANCED)
    # ------------------------------------------------
    if (
        skin > 0.65
        and scene.get("indoor", False)
        and not motion.get("aggressive_motion", False)
    ):
        if is_sexualized:
            risk = max(risk, 0.95)
            reasons.append("Very high skin exposure with sexualized indoor context")
        elif is_private:
            risk = max(risk, 0.85)
            reasons.append("Very high skin exposure in private indoor context")
        else:
            risk = max(risk, 0.7)
            reasons.append("Very high skin exposure in indoor context")

    # ------------------------------------------------
    # FALLBACK - HIGH SKIN WITH NO CONTEXT
    # ------------------------------------------------
    if skin > 0.5 and risk < 0.3:
        risk = max(risk, 0.4)
        reasons.append("High skin exposure - context unclear")

    return round(min(risk, 1.0), 3), reasons
