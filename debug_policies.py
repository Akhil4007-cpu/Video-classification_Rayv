#!/usr/bin/env python3
"""
Debug script to test policy evaluation for crash detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stage0_sampling.smart_sampler import smart_sample
from stage2_vision.blip_only import detect_objects_blip_only, classify_scene_blip_only
from stage2_vision.blip_scene import load_labels
from signals.signals_builder import build_signals
from policy_engine.evaluator import evaluate_policies
from policy_engine.aggregator import aggregate_risks

def test_crash_detection():
    video_path = "C:\\Users\\akhil\\Downloads\\istockphoto-948679414-640_adpp_is.mp4"
    
    print("🧪 Testing Crash Detection")
    print("=" * 50)
    
    # Sample frames
    frames = smart_sample(video_path)
    print(f"🎞️  Selected {len(frames)} frames")
    
    # BLIP analysis
    risky_objects, safe_objects = detect_objects_blip_only(frames)
    labels = load_labels("config/clip_labels.txt")
    scene_results, scene_types = classify_scene_blip_only(frames, labels)
    
    print(f"\n🔍 Risky Objects: {risky_objects}")
    print(f"🔍 Safe Objects: {safe_objects}")
    print(f"🔍 Scene Types: {scene_types}")
    
    # Build signals
    signals = build_signals(
        motion_score=32.97,
        risky_objects=risky_objects,
        safe_objects=safe_objects,
        scene_labels=scene_results,
        audio_score=0.0,
        temporal_state={"sustained": False, "impact_detected": False, "possible_accident": True},
        pose_signals={"human_present": True, "hands_detected": False, "hands_near_face": False, "hands_near_chest": False, "raised_arms": False},
        skin_ratio=0.1,
        blood_visible=True,
        fire_visible=False,
        scene_types=scene_types
    )
    
    print(f"\n🧪 ENTITY Signals: {signals['entity']}")
    
    # Evaluate policies
    risks = evaluate_policies(signals)
    
    print(f"\n📊 Policy Results:")
    for policy, result in risks.items():
        print(f"  {policy}: score={result['score']}, reasons={result['reasons']}")
    
    # Aggregate risks
    final_risk = aggregate_risks(risks)
    print(f"\n🎯 Final Risk: {final_risk}")

if __name__ == "__main__":
    test_crash_detection()
