def evaluate_accidents(signals):
    """
    Detect accidental events like falls or crashes.
    Cooking and food preparation must never be accidents.
    """

    # HARD BLOCK — COOKING
    if signals["entity"].get("food_present", False):
        return 0.0, []

    motion = signals["motion"]
    temporal = signals["temporal"]
    entity = signals["entity"]

    risk = 0.0
    reasons = []

    # HIGH RISK — VEHICLE CRASH
    if entity.get("crash_detected", False):
        risk = 0.8
        reasons.append("Vehicle crash detected")

    # MEDIUM RISK — POSSIBLE ACCIDENT
    elif (
        motion.get("sudden_motion", False)
        and temporal.get("possible_accident", False)
        and not entity.get("weapon_present", False)
    ):
        risk = 0.5
        reasons.append("Possible accident based on abnormal motion")

    return round(risk, 3), reasons
