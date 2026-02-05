def evaluate_fire_safety(signals):
    """
    Enhanced fire safety policy with BLIP context analysis.
    Focus on fire detection + context without complex scene analysis.
    
    Categories:
    - DANGEROUS: Fire + high motion/panic/emergency
    - REVIEW: Fire detected (needs human verification)
    - SAFE: No fire detected or controlled fire context
    
    Enhanced with BLIP descriptions to distinguish:
    - Dangerous fires vs campfires/cooking
    - Emergency situations vs recreational activities
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

    # ------------------------------------------------
    # BLIP FIRE CONTEXT ANALYSIS
    # ------------------------------------------------
    scene_labels = signals.get("scene_labels", [])
    descriptions = [label[0] if isinstance(label, tuple) else str(label) for label in scene_labels]
    fire_desc = " ".join(descriptions).lower()
    
    # Fire context detection
    dangerous_words = ["burning", "exploding", "out of control", "spreading", "wildfire", "emergency", "disaster"]
    emergency_words = ["emergency", "rescue", "firefighter", "alarm", "evacuation", "panic"]
    controlled_words = ["campfire", "bonfire", "fireplace", "controlled", "contained", "recreational"]
    cooking_words = ["cooking", "stove", "oven", "grill", "kitchen", "preparing food"]

    is_dangerous = any(word in fire_desc for word in dangerous_words)
    is_emergency = any(word in fire_desc for word in emergency_words)
    is_controlled = any(word in fire_desc for word in controlled_words)
    is_cooking = any(word in fire_desc for word in cooking_words)

    # 🔥 FIRE DETECTION
    fire_detected = visual.get("fire_visible", False)
    fire_objects = entity.get("fire_present", False)
    fire_mentioned = "fire" in fire_desc
    
    if not fire_detected and not fire_objects and not fire_mentioned:
        return 0.0, []  # No fire detected

    # ------------------------------------------------
    # ENHANCED CONTEXT-BASED RISK ASSESSMENT
    # ------------------------------------------------
    if is_dangerous or is_emergency:
        risk = max(risk, 0.8)
        reasons.append("Dangerous or emergency fire situation detected")
    
    elif fire_detected and motion.get("motion_score", 0) > 60:
        risk = max(risk, 0.8)
        reasons.append("High motion with fire indicates dangerous situation")
    
    elif is_controlled:
        risk = max(risk, 0.2)
        reasons.append("Controlled/recreational fire detected")
    
    elif is_cooking:
        risk = max(risk, 0.1)
        reasons.append("Cooking fire detected")
    
    elif fire_detected or fire_objects:
        # Fire detected but context unclear
        risk = max(risk, 0.4)
        reasons.append("Fire detected - context analysis needed")

    # ------------------------------------------------
    # LOCATION-BASED ASSESSMENT (ENHANCED)
    # ------------------------------------------------
    if scene.get("kitchen", False) and risk > 0.2:
        # Kitchen fire is usually cooking-related
        if not is_dangerous and not is_emergency:
            risk = min(risk, 0.2)
            reasons.append("Kitchen fire - likely cooking related")
    
    elif scene.get("outdoor", False) and risk < 0.7:
        # Outdoor fire could be campfire or wildfire
        if is_controlled:
            risk = max(risk, 0.3)
            reasons.append("Outdoor recreational fire")
        elif not is_dangerous:
            risk = max(risk, 0.3)
            reasons.append("Outdoor fire - context unclear")

    # ------------------------------------------------
    # AUDIO ENHANCEMENT
    # ------------------------------------------------
    if audio.get("panic_audio", False) and risk > 0.3:
        risk = min(risk + 0.2, 1.0)
        reasons.append("Panic audio confirms dangerous fire situation")

    # ------------------------------------------------
    # FINAL RISK ADJUSTMENT
    # ------------------------------------------------
    if risk >= 0.7:
        reasons.append("HIGH RISK - Immediate attention needed")
    elif risk >= 0.4:
        reasons.append("MODERATE RISK - Human review required")

    return round(min(risk, 1.0), 3), reasons
