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
    food_context = (
        len(safe_objects) > 0
        or any(
            kw in label.lower()
            for label, _ in scene_labels
            for kw in ["kitchen", "cooking", "food", "vegetable", "cutting"]
        )
    )

    human_present = (
        pose_signals.get("human_present", False)
        or skin_ratio > 0.15
        or motion_score > 10
    )

    return {
        "entity": {
            "knife_present": "knife" in risky_objects,
            "weapon_present": any(o in ["gun", "pistol", "rifle"] for o in risky_objects),
            "food_present": food_context,
            "vehicle_present": any(o in ["car", "bus", "truck"] for o in risky_objects),
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
