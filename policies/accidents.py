def evaluate_accidents(signals):
    """
    Detect accidental events like falls or crashes.
    Cooking and food preparation must never be accidents.
    Enhanced with BLIP context analysis.
    """

    # ------------------------------------------------
    # BLIP CONTEXT ANALYSIS
    # ------------------------------------------------
    scene_labels = signals.get("scene_labels", [])
    descriptions = [label[0] if isinstance(label, tuple) else str(label) for label in scene_labels]
    accident_desc = " ".join(descriptions).lower()
    
    # Cooking context detection
    cooking_words = ["cooking", "food", "tomato", "vegetable", "cutting", "preparing", "kitchen", "pepper", "cutting board", "wooden"]
    is_cooking_context = any(word in accident_desc for word in cooking_words)
    
    # Staged content detection
    staged_words = ["movie", "film", "scene", "trailer", "actor", "actress", "stunt", "performance"]
    is_staged = any(word in accident_desc for word in staged_words)

    # ------------------------------------------------
    # HARD BLOCK — COOKING (ENHANCED)
    # ------------------------------------------------
    if signals["entity"].get("food_present", False) or is_cooking_context:
        return 0.0, ["Cooking/food preparation context - safe"]

    motion = signals["motion"]
    temporal = signals["temporal"]
    entity = signals["entity"]

    risk = 0.0
    reasons = []

    # ------------------------------------------------
    # HIGH RISK — VEHICLE CRASH
    # ------------------------------------------------
    if entity.get("crash_detected", False):
        if is_staged:
            risk = max(risk, 0.3)  # Lower risk for staged crashes
            reasons.append("Staged vehicle crash detected")
        else:
            risk = 0.8
            reasons.append("Vehicle crash detected")

    # ------------------------------------------------
    # MEDIUM RISK — POSSIBLE ACCIDENT (ENHANCED)
    # ------------------------------------------------
    elif (
        motion.get("sudden_motion", False)
        and temporal.get("possible_accident", False)
        and not entity.get("weapon_present", False)
    ):
        if is_staged:
            risk = max(risk, 0.2)  # Very low risk for staged content
            reasons.append("Staged accident scene detected")
        else:
            risk = 0.5
            reasons.append("Possible accident based on abnormal motion")

    return round(risk, 3), reasons
