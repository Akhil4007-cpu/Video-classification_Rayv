import sys
import time
import warnings
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import numpy as np

# Suppress all warnings
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

from vision.pose_detector import PoseAnalyzer
from vision.skin_detector import detect_skin_ratio
from vision.blood_detector import detect_blood
from vision.fire_detector import detect_fire
from vision.human_segmenter import detect_human

from stage0_sampling.smart_sampler import smart_sample
from stage1_fast_filter.motion_filter import fast_filter, motion_risk_score
from stage2_vision.blip_only import detect_objects_blip_only, classify_scene_blip_only
from stage3_temporal.temporal_brain import TemporalBrain
from stage6_audio.audio_utils import extract_audio
from stage6_audio.audio_analyzer import analyze_audio

from signals.signals_builder import build_signals
from policy_engine.evaluator import evaluate_policies
from policy_engine.aggregator import aggregate_risks


def analyze_video(video_path):
    """Optimized video analysis with parallel processing - preserves original behavior"""
    start_time = time.time()
    print("\n📥 Loading video:", video_path)

    # ---------------- STAGE 0 ----------------
    frames = smart_sample(video_path)
    print(f"🎞️  Stage 0: Selected {len(frames)} key frames")

    # ---------------- STAGE 1 ----------------
    fast_flag, fast_info = fast_filter(frames)
    print(f"⚡ Stage 1: Fast suspicious =", fast_flag, fast_info)

    brain = TemporalBrain(window_size=5)

    all_risky_objects = set()
    all_safe_objects = set()
    all_scene_labels = []

    pose_analyzer = PoseAnalyzer()
    pose_signals = {
        "human_present": False,
        "hands_detected": False,
        "hands_near_face": False,
        "hands_near_chest": False,
        "raised_arms": False
    }

    skin_ratios = []
    blood_detected = False
    fire_detected = False
    human_detected = False

    # ---------------- FRAME PROCESSING (OPTIMIZED) ----------------
    print("🔄 Processing frames with parallel vision analysis...")
    
    all_motion_scores = []
    all_pose_data = []
    all_skin_ratios = []
    
    # Process frames in parallel for vision tasks
    def process_frame_vision(frame_data):
        frame, idx = frame_data
        results = {}
        
        try:
            # Process vision tasks for this frame
            results['motion'] = motion_risk_score([frame])
            results['pose'] = pose_analyzer.analyze(frame)
            results['skin_ratio'] = detect_skin_ratio(frame)
            results['blood'] = detect_blood(frame)
            results['fire'] = detect_fire(frame)
            results['human'] = detect_human(frame)
            
            print(f"✅ Frame {idx} processed")
            
        except Exception as e:
            print(f"⚠️  Error processing frame {idx}: {str(e)}")
            # Set defaults
            results = {
                'motion': 0.0,
                'pose': {},
                'skin_ratio': 0.0,
                'blood': False,
                'fire': False,
                'human': False
            }
        
        return results
    
    # Process frames in parallel
    max_workers = min(len(frames), 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        frame_futures = {
            executor.submit(process_frame_vision, (frame, i)): i 
            for i, frame in enumerate(frames)
        }
        
        for future in as_completed(frame_futures, timeout=60):
            frame_idx = frame_futures[future]
            try:
                frame_results = future.result(timeout=15)
                
                # Collect results
                all_motion_scores.append(frame_results['motion'])
                all_pose_data.append(frame_results['pose'])
                all_skin_ratios.append(frame_results['skin_ratio'])
                
                if frame_results['blood']:
                    blood_detected = True
                
                if frame_results['fire']:
                    fire_detected = True
                
                if frame_results['human']:
                    human_detected = True
                
                # Add to temporal brain
                brain.add_frame_result(
                    motion_score=frame_results['motion'],
                    risky_objects=[],
                    safe_objects=[],
                    clip_results=[]
                )
                
            except Exception as e:
                print(f"⚠️  Timeout or error in frame {frame_idx}: {str(e)}")
                continue

    # ---------------- BATCH BLIP PROCESSING ----------------
    print("🚀 Processing frames with BLIP (TRUE BATCH MODE)...")
    risky_objects, safe_objects = detect_objects_blip_only(frames)
    all_scene_results, scene_types = classify_scene_blip_only(frames)
    
    # Aggregate results
    all_risky_objects.update(risky_objects)
    all_safe_objects.update(safe_objects)
    all_scene_labels.extend(all_scene_results)
    
    # Aggregate pose signals (ORIGINAL LOGIC)
    for pose in all_pose_data:
        for k in pose_signals:
            pose_signals[k] |= pose.get(k, False)

    pose_signals["human_present"] |= human_detected
    avg_skin = sum(all_skin_ratios) / len(all_skin_ratios) if all_skin_ratios else 0.0

    # ---------------- AUDIO ----------------
    audio_path = extract_audio(video_path)
    audio_score = analyze_audio(audio_path)["risk_score"] if audio_path else 0.0
    print("🔊 Audio risk:", audio_score)

    temporal_state = {
        "sustained": brain.intent_score() > 0.3,
        "impact_detected": brain.detect_impact()
    }

    # Build signals (ORIGINAL STRUCTURE)
    signals = build_signals(
        motion_score=fast_info["motion_score"],
        risky_objects=list(all_risky_objects),
        safe_objects=list(all_safe_objects),
        scene_labels=all_scene_labels,
        audio_score=audio_score,
        temporal_state=temporal_state,
        pose_signals=pose_signals,
        skin_ratio=avg_skin,
        blood_visible=blood_detected,
        fire_visible=fire_detected,
        scene_types=scene_types
    )

    print("\n🧪 DEBUG SIGNALS")
    for k, v in signals.items():
        print(k.upper(), ":", v)

    risks = evaluate_policies(signals)
    decision, explanation = aggregate_risks(risks)

    print("\n================ FINAL RESULT ================")
    print("📌 DECISION :", decision)
    print("🧾 DETAILS  :", explanation)
    print("⏱️  TIME    :", round(time.time() - start_time, 2), "seconds")
    print("=============================================\n")

    return decision, explanation


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python analyze_video_optimized.py <video_path>")
        sys.exit(1)

    analyze_video(sys.argv[1])
