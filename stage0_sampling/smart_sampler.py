import cv2
import numpy as np
from collections import deque

def smart_sample(
    video_path,
    motion_thresh=15,   # Lower threshold for better sensitivity
    scene_thresh=25,    # Lower threshold for scene change detection
    min_gap=10,         # Larger gap to avoid similar frames
    max_frames=8,       # Fewer frames to avoid redundancy
    similarity_thresh=0.95  # Similarity threshold for frame deduplication
):
    cap = cv2.VideoCapture(video_path)
    
    # Get video duration to adjust sampling strategy
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # More conservative frame allocation to avoid redundancy
    if duration > 0:
        if duration <= 10:      # Very short videos
            target_frames = min(3, total_frames)
        elif duration <= 30:    # Short videos  
            target_frames = min(5, total_frames)
        elif duration <= 60:    # 1 minute videos
            target_frames = min(8, total_frames)
        elif duration <= 180:   # 3 minute videos
            target_frames = min(12, total_frames)
        else:                   # Long videos
            target_frames = min(15, total_frames)
        
        max_frames = max(target_frames, max_frames)
    
    selected_frames = []
    prev_gray = None
    frame_idx = 0
    last_selected = -min_gap
    
    # Frame deduplication using structural similarity
    frame_history = deque(maxlen=5)  # Keep last 5 frames for comparison
    
    def is_similar_to_selected(frame, selected_frames, threshold=0.95):
        """Check if frame is too similar to already selected frames"""
        if not selected_frames:
            return False
            
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.resize(frame_gray, (64, 64))  # Resize for faster comparison
        
        for selected_frame in selected_frames[-3:]:  # Compare with last 3 selected frames
            selected_gray = cv2.cvtColor(selected_frame, cv2.COLOR_BGR2GRAY)
            selected_gray = cv2.resize(selected_gray, (64, 64))
            
            # Calculate structural similarity
            correlation = cv2.matchTemplate(frame_gray, selected_gray, cv2.TM_CCOEFF_NORMED)
            max_corr = np.max(correlation)
            
            if max_corr > threshold:
                return True
        
        return False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            motion_score = np.mean(diff)

            scene_score = np.mean(
                np.abs(gray.astype("float") - prev_gray.astype("float"))
            )

            # Enhanced criteria with frame deduplication
            should_select = (
                motion_score > motion_thresh or
                scene_score > scene_thresh or
                frame_idx - last_selected >= (duration * fps / max_frames if duration > 0 else 45)  # Less frequent forced selection
            )
            
            if should_select and frame_idx - last_selected >= min_gap:
                # Check for similarity with already selected frames
                if not is_similar_to_selected(frame, selected_frames, similarity_thresh):
                    selected_frames.append(frame)
                    last_selected = frame_idx
                    print(f"📹 Selected frame {frame_idx} (motion: {motion_score:.1f}, scene: {scene_score:.1f})")
                else:
                    print(f"⏭️  Skipping similar frame {frame_idx}")

        prev_gray = gray
        frame_idx += 1

        if len(selected_frames) >= max_frames:
            break

    cap.release()
    
    # If no frames were selected (e.g., very short video), take at least 1 frame
    if not selected_frames:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            selected_frames.append(frame)
            print(f"📹 Selected single frame (no motion detected)")
        cap.release()
    
    print(f"🎯 Selected {len(selected_frames)} unique frames from {total_frames} total frames")
    return selected_frames
