import sys
import time
import warnings
import logging
import os

# Suppress all warnings
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'  # Suppress HuggingFace telemetry
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'  # Suppress transformers warnings

from vision.pose_detector import PoseAnalyzer
from vision.skin_detector import detect_skin_ratio
from vision.blood_detector import detect_blood
from vision.fire_detector import detect_fire
from vision.human_segmenter import detect_human


from stage0_sampling.smart_sampler import smart_sample
from stage1_fast_filter.motion_filter import fast_filter, motion_risk_score
from stage2_vision.blip_only import detect_objects_blip_only, classify_scene_blip_only
from stage2_vision.blip_scene import load_labels
from stage3_temporal.temporal_brain import TemporalBrain
from stage6_audio.audio_utils import extract_audio
from stage6_audio.audio_analyzer import analyze_audio

from signals.signals_builder import build_signals
from policy_engine.evaluator import evaluate_policies
from policy_engine.aggregator import aggregate_risks


def analyze_video(video_path):
    start_time = time.time()
    print("\n📥 Loading video:", video_path)

    # ---------------- STAGE 0 ----------------
    frames = smart_sample(video_path)
    print(f"🎞️  Stage 0: Selected {len(frames)} key frames")

    # ---------------- STAGE 1 ----------------
    fast_flag, fast_info = fast_filter(frames)
    print(f"⚡ Stage 1: Fast suspicious =", fast_flag, fast_info)

    labels = load_labels("config/clip_labels.txt")
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

    # ---------------- FRAME PROCESSING ----------------
    # Batch BLIP processing for maximum speed
    scene_types = {"kitchen": False, "outdoor": False, "indoor": False}
    
    # Process all frames with other detectors first
    all_motion_scores = []
    all_pose_data = []
    all_skin_ratios = []
    
    for frame in frames:
        motion = motion_risk_score([frame])
        all_motion_scores.append(motion)
        
        pose = pose_analyzer.analyze(frame)
        all_pose_data.append(pose)
        
        skin_ratios.append(detect_skin_ratio(frame))

        if detect_blood(frame):
            blood_detected = True

        if detect_fire(frame):
            fire_detected = True

        if detect_human(frame):
            human_detected = True
        
        brain.add_frame_result(
            motion_score=motion,
            risky_objects=[],
            safe_objects=[],
            clip_results=[]
        )
    
    # ---------------- BATCH BLIP PROCESSING ----------------
    print("🚀 Processing frames with BLIP (TRUE BATCH MODE)...")
    risky_objects, safe_objects = detect_objects_blip_only(frames)
    all_scene_results, scene_types = classify_scene_blip_only(frames, labels)
    
    # Aggregate results
    all_risky_objects.update(risky_objects)
    all_safe_objects.update(safe_objects)
    all_scene_labels.extend(all_scene_results)
    
    # Aggregate pose signals
    for pose in all_pose_data:
        for k in pose_signals:
            pose_signals[k] |= pose.get(k, False)

    pose_signals["human_present"] |= human_detected
    avg_skin = sum(skin_ratios) / len(skin_ratios) if skin_ratios else 0.0

    # ---------------- AUDIO ----------------
    audio_path = extract_audio(video_path)
    audio_score = analyze_audio(audio_path)["risk_score"] if audio_path else 0.0
    print("🔊 Audio risk:", audio_score)

    temporal_state = {
        "sustained": brain.intent_score() > 0.3,
        "impact_detected": brain.detect_impact()
    }

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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python analyze_video.py <video_path>")
        sys.exit(1)

    analyze_video(sys.argv[1])
