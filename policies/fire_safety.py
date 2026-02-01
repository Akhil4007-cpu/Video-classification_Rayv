def evaluate_fire_safety(signals):
    """
    Simplified fire safety policy.
    Focus on fire detection + context without complex scene analysis.
    
    Categories:
    - DANGEROUS: Fire + high motion/panic
    - REVIEW: Fire detected (needs human verification)
    - SAFE: No fire detected
    """

    risk = 0.0
    reasons = []

    human = signals.get("human", {})
    motion = signals.get("motion", {})
    visual = signals.get("visual_state", {})
    audio = signals.get("audio", {})
    scene = signals.get("scene", {})
    entity = signals.get("entity", {})

    if not human.get("human_present", False):
        return 0.0, []

    # 🔥 FIRE DETECTION
    fire_detected = visual.get("fire_visible", False)
    fire_objects = entity.get("fire_present", False)
    
    if not fire_detected and not fire_objects:
        return 0.0, []  # No fire detected

    #  IMMEDIATE DANGER SIGNALS
    if (
        audio.get("panic_audio", False)
        or motion.get("motion_score", 0) > 60  # Very high motion
    ):
        risk = max(risk, 0.8)
        reasons.append("Dangerous fire activity detected")
    
    # ⚠️ FIRE DETECTED - NEEDS REVIEW
    else:
        risk = max(risk, 0.4)
        reasons.append("Fire detected - requires human review")

    # 📍 LOCATION-BASED ASSESSMENT
    if scene.get("kitchen", False):
        # Kitchen fire is usually cooking-related
        if risk > 0.3:
            risk = min(risk, 0.3)
            reasons.append("Kitchen fire - likely cooking related")
    
    elif scene.get("outdoor", False):
        # Outdoor fire could be campfire or wildfire
        if risk < 0.6:  # Don't reduce if already high risk
            risk = max(risk, 0.3)
            reasons.append("Outdoor fire - context unclear")

    # 🎯 FINAL RISK ADJUSTMENT
    if risk >= 0.7:
        reasons.append("HIGH RISK - Immediate attention needed")
    elif risk >= 0.4:
        reasons.append("MODERATE RISK - Human review required")

    return round(min(risk, 1.0), 3), reasons
