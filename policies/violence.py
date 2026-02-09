def evaluate_violence(signals):
    """
    Intent-aware violence detection with BLIP context analysis.

    Detects:
    - Weapon-based violence
    - Hand-to-hand fighting
    - Blood with aggressive intent

    Avoids false positives from:
    - Cooking (tomato, meat, food prep)
    - Non-violent red visuals
    - Movie/staged content
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
    scene = signals.get("scene", {})

    # ------------------------------------------------
    # BLIP CONTEXT ANALYSIS
    # ------------------------------------------------
    scene_labels = signals.get("scene_labels", [])
    descriptions = [label[0] if isinstance(label, tuple) else str(label) for label in scene_labels]
    
    # Detect staged/movie content
    staged_indicators = ["movie", "film", "scene", "trailer", "actor", "actress", "stunt", "performance"]
    is_staged = any(indicator in " ".join(descriptions).lower() for indicator in staged_indicators)
    
    # Detect actual violence context
    violence_words = ["fight", "fighting", "punch", "hit", "attack", "assault", "beat", "strike", "violent"]
    has_violence_desc = any(word in " ".join(descriptions).lower() for word in violence_words)

    # ------------------------------------------------
    # HARD BLOCK — NO HUMAN
    # ------------------------------------------------
    if not human.get("human_present", False):
        return 0.0, []

    # ------------------------------------------------
    # WEAPON-BASED VIOLENCE (ENHANCED)
    # ------------------------------------------------
    if entity.get("weapon_present", False):
        if is_staged:
            risk = max(risk, 0.3)  # Much lower risk for staged content
            reasons.append("Weapons in staged/movie context")
        elif has_violence_desc and motion.get("aggressive_motion", False):
            risk = max(risk, 0.9)
            reasons.append("Weapon present with violent intent and aggressive motion")
        elif motion.get("aggressive_motion", False):
            risk = max(risk, 0.8)
            reasons.append("Weapon present with aggressive motion")
        else:
            risk = max(risk, 0.5)
            reasons.append("Weapon detected - context unclear")

    # ------------------------------------------------
    # HAND-TO-HAND FIGHTING (ENHANCED)
    # ------------------------------------------------
    if (
        motion.get("aggressive_motion", False)
        and pose.get("hands_detected", False)
        and pose.get("raised_arms", False)
        and not entity.get("food_present", False)
    ):
        if is_staged:
            risk = max(risk, 0.4)
            reasons.append("Fighting in staged context")
        elif has_violence_desc:
            risk = max(risk, 0.85)
            reasons.append("Aggressive fighting with violent descriptions")
        else:
            risk = max(risk, 0.7)
            reasons.append("Aggressive human motion consistent with fighting")

    # ------------------------------------------------
    # COOKING CONTEXT OVERRIDE (CRITICAL FIX)
    # ------------------------------------------------
    # If BLIP detects cooking context, immediately return SAFE - this prevents false positives
    cooking_words = ["cooking", "food", "tomato", "vegetable", "cutting", "preparing", "kitchen", "pepper", "cutting board", "wooden"]
    violence_desc = " ".join(descriptions).lower()
    is_cooking_context = any(word in violence_desc for word in cooking_words)
    
    if is_cooking_context:
        return 0.0, ["Cooking/food preparation context - safe"]
    
    # ------------------------------------------------
    # SPORTS CONTEXT OVERRIDE (NEW)
    # ------------------------------------------------
    # If BLIP detects sports context, immediately return SAFE
    sports_words = ["sport", "game", "playing", "athlete", "competition", "training", "exercise", "workout", "soccer", "basketball", "football", "tennis", "running", "swimming", "gym"]
    is_sports_context = any(word in violence_desc for word in sports_words)
    
    if is_sports_context:
        return 0.0, ["Sports activity - safe"]

    # ------------------------------------------------
    # BLOOD CONFIRMATION (ENHANCED WITH BLIP)
    # ------------------------------------------------
    if visual.get("blood_visible", False):
        
        # Analyze blood context from descriptions
        blood_desc = violence_desc
        cooking_words = ["cooking", "food", "tomato", "sauce", "kitchen", "cutting", "preparing"]
        injury_words = ["injury", "wound", "bleeding", "hurt", "accident", "cut", "stab"]
        
        is_cooking_context = any(word in blood_desc for word in cooking_words)
        is_injury_context = any(word in blood_desc for word in injury_words)

        # 🛑 Blood + food context → NOT violence
        if (
            entity.get("food_present", False)
            and scene.get("kitchen", False)
            and not audio.get("panic_audio", False)
            and motion.get("motion_score", 0) < 30
        ) or is_cooking_context:
            risk = max(risk, 0.1)
            reasons.append("Red fluid in cooking context")

        # 🚨 Blood + aggressive intent → violence
        elif (
            motion.get("aggressive_motion", False)
            and pose.get("raised_arms", False)
        ) or is_injury_context:
            if is_staged:
                risk = max(risk, 0.4)
                reasons.append("Injury in staged context")
            else:
                risk = max(risk, 0.9)
                reasons.append("Visible blood with aggressive intent")

        # ⚠️ Blood but unclear intent → REVIEW
        else:
            risk = max(risk, 0.3)
            reasons.append("Blood-like visual detected (requires review)")

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
