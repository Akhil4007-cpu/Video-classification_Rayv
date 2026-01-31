def evaluate_self_harm(signals):
    """
    Detect self-harm behavior.
    Conservative, human-centered, temporal-aware.
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

    # ----------------------------------------
    # HARD BLOCKS (IMPORTANT)
    # ----------------------------------------

    # No human → no self-harm
    if not human.get("human_present", False):
        return 0.0, []

    # Cooking / food context → NOT self-harm
    if entity.get("food_present", False):
        return 0.0, []

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

    # Sharp object + body-focused pose
    if (
        entity.get("knife_present", False)
        and (
            pose.get("hands_near_chest", False)
            or pose.get("hands_near_face", False)
        )
        and not motion.get("aggressive_motion", False)
    ):
        risk = max(risk, 0.7)
        reasons.append("Sharp object used near own body")

    # ----------------------------------------
    # TEMPORAL CONFIRMATION (VERY IMPORTANT)
    # ----------------------------------------
    if temporal.get("sustained", False) and risk > 0.5:
        risk = min(risk + 0.2, 1.0)
        reasons.append("Sustained self-harm behavior over time")

    return round(min(risk, 1.0), 3), reasons
