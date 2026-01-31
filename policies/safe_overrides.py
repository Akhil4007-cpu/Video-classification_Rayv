def apply_safe_overrides(risk_score, reasons, signals):
    """
    Apply safe-context reductions.
    NEVER cancels confirmed violence or self-harm.
    """

    # If no risk, nothing to do
    if risk_score <= 0.0:
        return risk_score, reasons

    entity = signals.get("entity", {})
    scene = signals.get("scene", {})
    audio = signals.get("audio", {})
    motion = signals.get("motion", {})
    visual = signals.get("visual_state", {})
    pose = signals.get("pose", {})
    human = signals.get("human", {})

    # ======================================================
    # 🚨 HARD BLOCK — NEVER OVERRIDE CONFIRMED HARM
    # ======================================================
    if (
        visual.get("blood_visible", False)
        and (
            motion.get("aggressive_motion", False)
            or pose.get("raised_arms", False)
            or entity.get("weapon_present", False)
        )
    ):
        return round(risk_score, 3), reasons
    
    # Allow overrides for blood without aggressive intent
    if (
        visual.get("blood_visible", False)
        and not motion.get("aggressive_motion", False)
        and not pose.get("raised_arms", False)
        and not entity.get("weapon_present", False)
    ):
        # Continue to safe overrides - this might be false positive
        pass
    elif (
        motion.get("aggressive_motion", False)
        or pose.get("raised_arms", False)
        or entity.get("crash_detected", False)
    ):
        return round(risk_score, 3), reasons

    # ======================================================
    # 🎥 SPEAKING / PRESENTATION CONTEXT (NEW)
    # ======================================================
    if (
        human.get("human_present", False)
        and not entity.get("weapon_present", False)
        and not entity.get("crash_detected", False)
        and motion.get("motion_score", 0) < 20  # Low motion
        and not audio.get("panic_audio", False)
        and not scene.get("kitchen", False)  # Not in kitchen
    ):
        risk_score *= 0.3
        reasons.append("Speaking/presentation context")

    # ======================================================
    # �� COOKING CONTEXT (REDUCTION, NOT RESET)
    # ======================================================
    if (
        entity.get("knife_present", False)
        and entity.get("food_present", False)
        and scene.get("kitchen", False)
        and not audio.get("panic_audio", False)
        and motion.get("motion_score", 0) < 40
    ):
        risk_score *= 0.3
        reasons.append("Safe cooking context")

    # ======================================================
    # 🏃 SPORTS / TRAINING CONTEXT
    # ======================================================
    if (
        motion.get("motion_score", 0) > 35
        and not entity.get("weapon_present", False)
        and scene.get("outdoor", False)
        and not audio.get("panic_audio", False)
    ):
        risk_score *= 0.6
        reasons.append("Likely sports or physical activity")

    # ======================================================
    # 🏥 MEDICAL / FIRST-AID CONTEXT
    # ======================================================
    if (
        entity.get("knife_present", False)
        and scene.get("indoor", False)
        and not audio.get("panic_audio", False)
        and motion.get("motion_score", 0) < 30
    ):
        risk_score *= 0.5
        reasons.append("Possible medical or first-aid context")

    # ======================================================
    # 🏖️ BEACH / PUBLIC SKIN CONTEXT
    # ======================================================
    if (
        visual.get("skin_exposure_ratio", 0.0) > 0.3
        and scene.get("outdoor", False)
        and scene.get("public_space", False)
        and not audio.get("panic_audio", False)
    ):
        risk_score *= 0.4
        reasons.append("Public / beach context with normal skin exposure")

    # ======================================================
    # 🚶 CONTROLLED PUBLIC ACTIVITY
    # ======================================================
    if (
        not audio.get("panic_audio", False)
        and scene.get("public_space", False)
        and motion.get("motion_score", 0) < 30
    ):
        risk_score *= 0.7
        reasons.append("Controlled public activity")

    return round(max(risk_score, 0.0), 3), reasons
