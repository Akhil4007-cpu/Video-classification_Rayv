def build_signals(
    motion_score,
    risky_objects,
    safe_objects,
    scene_labels,
    audio_score,
    temporal_state,
    pose_signals,
    skin_ratio,
    blood_visible,
    fire_visible,
    scene_types
):
    # ---------------- FOOD CONTEXT ----------------
    crash_detected = any(obj in ["vehicle_crash", "accident", "crash"] for obj in risky_objects)
    
    # Much stricter food context detection - require explicit food indicators
    food_keywords = ["kitchen", "cooking", "food", "vegetable", "cutting", "chef", "recipe", "meal", "dinner", "lunch", "breakfast", "restaurant", "tomato", "pepper"]
    cooking_objects = ["knife", "cutting_board", "pot", "pan", "stove", "oven", "grill", "mixing_bowl", "spatula", "fork", "spoon", "food", "vegetable"]
    
    # Require scene description OR objects to indicate cooking (more lenient)
    scene_has_food = any(
        kw in label.lower()
        for label, _ in scene_labels
        for kw in food_keywords
    )
    
    objects_have_food = any(obj in safe_objects for obj in cooking_objects)
    
    food_context = (
        not crash_detected 
        and (scene_has_food or objects_have_food)
    )

    human_present = (
        pose_signals.get("human_present", False)
        or skin_ratio > 0.15
        or motion_score > 10
    )

    return {
        "entity": {
            "knife_present": "knife" in risky_objects or any("cutting" in label.lower() for label, _ in scene_labels),
            "weapon_present": any(o in ["gun", "pistol", "rifle"] for o in risky_objects),
            "food_present": food_context,
            "vehicle_present": any(o in ["car", "bus", "truck", "vehicle_crash", "accident"] for o in risky_objects),
            "crash_detected": crash_detected,
        },

        "human": {
            "human_present": human_present,
            "adult_present": True,
            "child_present": False
        },

        "pose": pose_signals,

        "scene": {
            "kitchen": scene_types.get("kitchen", False),
            "indoor": scene_types.get("indoor", False),
            "outdoor": scene_types.get("outdoor", False),
        },

        "motion": {
            "motion_score": motion_score,
            "aggressive_motion": motion_score > 35,
            "sudden_motion": motion_score > 25,
        },

        "visual_state": {
            "blood_visible": blood_visible and not fire_visible,
            "fire_visible": fire_visible,
            "skin_exposure_ratio": skin_ratio,
        },

        "audio": {
            "audio_risk": audio_score,
            "panic_audio": audio_score > 0.6,
        },

        "temporal": {
            **temporal_state,
            "possible_accident": motion_score > 20 and not temporal_state["impact_detected"]
        }
    }
