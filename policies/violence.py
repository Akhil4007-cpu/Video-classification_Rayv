def evaluate_violence(signals):
    """
    Intent-aware violence detection.

    Detects:
    - Weapon-based violence
    - Hand-to-hand fighting
    - Blood with aggressive intent

    Avoids false positives from:
    - Cooking (tomato, meat, food prep)
    - Non-violent red visuals
    """

    risk = 0.0
    reasons = []

    human = signals.get("human", {})
    motion = signals.get("motion", {})
    entity = signals.get("entity", {})
    pose = signals.get("pose", {})
    visual = signals.get("visual_state", {})
    temporal = signals.get("temporal", {})
    audio = signals.get("audio", {})

    # ------------------------------------------------
    # HARD BLOCK — NO HUMAN
    # ------------------------------------------------
    if not human.get("human_present", False):
        return 0.0, []

    # ------------------------------------------------
    # WEAPON-BASED VIOLENCE
    # ------------------------------------------------
    if (
        entity.get("weapon_present", False)
        and motion.get("aggressive_motion", False)
    ):
        risk = max(risk, 0.85)
        reasons.append("Weapon present with aggressive motion")

    # ------------------------------------------------
    # HAND-TO-HAND FIGHTING
    # ------------------------------------------------
    if (
        motion.get("aggressive_motion", False)
        and pose.get("hands_detected", False)
        and pose.get("raised_arms", False)
        and not entity.get("food_present", False)
    ):
        risk = max(risk, 0.7)
        reasons.append("Aggressive human motion consistent with fighting")

    # ------------------------------------------------
    # BLOOD CONFIRMATION (FINAL INTENT-AWARE LOGIC)
    # ------------------------------------------------
    if visual.get("blood_visible", False):

        # 🛑 Blood + food context → NOT violence
        if (
            entity.get("food_present", False)
            and not audio.get("panic_audio", False)
        ):
            risk = max(risk, 0.2)
            reasons.append("Red fluid detected with food context (likely cooking)")

        # 🚨 Blood + aggressive intent → violence
        elif (
            motion.get("aggressive_motion", False)
            and pose.get("raised_arms", False)
        ):
            risk = max(risk, 0.9)
            reasons.append("Visible blood with aggressive intent")

        # ⚠️ Blood but unclear intent → REVIEW
        else:
            risk = max(risk, 0.4)
            reasons.append("Blood-like visual detected (ambiguous context)")

    # ------------------------------------------------
    # AUDIO ESCALATION
    # ------------------------------------------------
    if audio.get("panic_audio", False) and risk > 0.4:
        risk = min(risk + 0.15, 1.0)
        reasons.append("Panic or distress audio detected")

    # ------------------------------------------------
    # TEMPORAL CONFIRMATION
    # ------------------------------------------------
    if temporal.get("sustained", False) and risk > 0.4:
        risk = min(risk + 0.15, 1.0)
        reasons.append("Sustained violent behavior")

    return round(min(risk, 1.0), 3), reasons
