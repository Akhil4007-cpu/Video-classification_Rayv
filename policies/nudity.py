def evaluate_nudity(signals):
    """
    Intent-aware nudity detection.
    Requires sexualized context, not just skin exposure.
    """

    risk = 0.0
    reasons = []

    human = signals.get("human", {})
    visual = signals.get("visual_state", {})
    scene = signals.get("scene", {})
    pose = signals.get("pose", {})
    motion = signals.get("motion", {})

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
    # OUTDOOR / PUBLIC CONTEXT (NON-SEXUAL)
    # ------------------------------------------------
    if scene.get("outdoor", False) and skin < 0.5:
        return 0.0, []

    # ------------------------------------------------
    # SEXUALIZED NUDITY (CORE LOGIC)
    # ------------------------------------------------
    if (
        skin > 0.35
        and (
            pose.get("hands_near_chest", False)
            or pose.get("hands_near_face", False)
        )
        and not motion.get("aggressive_motion", False)
    ):
        risk = 0.75
        reasons.append("Sexualized pose with skin exposure")

    # ------------------------------------------------
    # VERY HIGH SKIN + INDOOR (STILL NEED CALM CONTEXT)
    # ------------------------------------------------
    if (
        skin > 0.65
        and scene.get("indoor", False)
        and not motion.get("aggressive_motion", False)
    ):
        risk = max(risk, 0.85)
        reasons.append("Very high skin exposure in private indoor context")

    return round(min(risk, 1.0), 3), reasons
