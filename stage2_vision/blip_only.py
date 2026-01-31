from stage2_vision.blip_scene import batch_process_frames

# Object detection using BLIP-1 descriptions only (batch optimized)
def detect_objects_blip_only(frames):
    """
    Object detection using only BLIP-1 descriptions (batch processing)
    """
    # Get all descriptions at once
    descriptions = batch_process_frames(frames)
    
    all_risky_objects = []
    all_safe_objects = []
    
    for description in descriptions:
        risky_objects = []
        safe_objects = []
        
        desc_lower = description.lower()
        
        # Risk objects detection
        if any(word in desc_lower for word in ["gun", "weapon", "knife", "rifle", "pistol"]):
            if "knife" in desc_lower and ("cooking" in desc_lower or "food" in desc_lower):
                # Kitchen knife - safe context
                safe_objects.append("knife")
            else:
                # Weapon or dangerous knife
                risky_objects.append("knife")
        
        if any(word in desc_lower for word in ["gun", "rifle", "pistol"]):
            risky_objects.append("gun")
        
        # Vehicle and crash detection
        if any(word in desc_lower for word in ["car", "vehicle", "truck", "automobile"]):
            if any(word in desc_lower for word in ["crash", "accident", "collision", "wreck", "smash", "hit"]):
                risky_objects.append("vehicle_crash")
                risky_objects.append("accident")
            else:
                safe_objects.append("vehicle")
        
        # Fire and explosion detection
        if any(word in desc_lower for word in ["fire", "flame", "explosion", "burning"]):
            risky_objects.append("fire")
        
        # Violence detection
        if any(word in desc_lower for word in ["fight", "attack", "violence", "assault", "punch"]):
            risky_objects.append("violence")
        
        # Safe objects detection (but exclude if crash detected)
        crash_detected = any(word in desc_lower for word in ["crash", "accident", "collision", "wreck"])
        if not crash_detected:
            if any(word in desc_lower for word in ["tomato", "vegetable", "food", "cooking", "kitchen"]):
                safe_objects.extend(["food", "vegetable"])
                if "cooking" in desc_lower or "kitchen" in desc_lower:
                    safe_objects.append("kitchen")
        
        all_risky_objects.extend(risky_objects)
        all_safe_objects.extend(safe_objects)
        
        print(f"🔍 BLIP Objects: risky={risky_objects}, safe={safe_objects}")
        print(f"📝 Description: {description}")
    
    # Return unique objects
    return list(set(all_risky_objects)), list(set(all_safe_objects))

# Scene classification using BLIP-1 only (batch optimized)
def classify_scene_blip_only(frames, labels):
    """
    Scene classification using only BLIP-1 descriptions (batch processing)
    """
    # Get all descriptions at once
    descriptions = batch_process_frames(frames)
    
    all_scene_results = []
    all_scene_types = {"kitchen": False, "outdoor": False, "indoor": False}
    
    for description in descriptions:
        desc_lower = description.lower()
        
        # Scene type detection
        scene_types = {
            "kitchen": any(word in desc_lower for word in ["kitchen", "cooking", "food", "tomatoes", "vegetables"]),
            "outdoor": any(word in desc_lower for word in ["woods", "outdoor", "outside", "nature", "wood", "trees"]),
            "indoor": any(word in desc_lower for word in ["kitchen", "room", "inside", "indoor", "home"])
        }
        
        # Aggregate scene types
        for key in all_scene_types:
            all_scene_types[key] |= scene_types[key]
        
        # Label scoring
        scene_scores = []
        for label in labels:
            label_lower = label.lower()
            score = 0.0
            
            if any(word in desc_lower for word in label_lower.split() if len(word) > 2):
                score = 0.7
                
            if "violent" in label_lower and ("fight" in desc_lower or "attack" in desc_lower):
                score = 0.9
            elif "cooking" in label_lower and any(kw in desc_lower for kw in ["kitchen", "cooking", "food"]):
                score = 0.9
                
            scene_scores.append(score)
        
        # Normalize scores
        if max(scene_scores) > 0:
            scene_scores = [s/max(scene_scores) for s in scene_scores]
        
        all_scene_results.extend(list(zip(labels, scene_scores)))
        
        print(f"🔍 BLIP Scene: {scene_types}")
    
    return all_scene_results, all_scene_types
