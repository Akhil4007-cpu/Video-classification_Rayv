import cv2
import numpy as np

def smart_sample(
    video_path,
    motion_thresh=15,   # Lower threshold for better sensitivity
    scene_thresh=25,    # Lower threshold for scene change detection
    min_gap=5,          # Smaller gap for more frames
    max_frames=15       # More frames for better coverage
):
    cap = cv2.VideoCapture(video_path)
    
    # Get video duration to adjust sampling strategy
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # Dynamic frame allocation based on video duration
    if duration > 0:
        if duration <= 10:      # Very short videos
            target_frames = min(5, total_frames)
        elif duration <= 30:    # Short videos  
            target_frames = min(8, total_frames)
        elif duration <= 60:    # 1 minute videos
            target_frames = min(12, total_frames)
        elif duration <= 180:   # 3 minute videos
            target_frames = min(20, total_frames)
        else:                   # Long videos
            target_frames = min(25, total_frames)
        
        max_frames = max(target_frames, max_frames)
    
    selected_frames = []
    prev_gray = None
    frame_idx = 0
    last_selected = -min_gap

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

            # More responsive criteria for scene changes and cuts
            if (
                motion_score > motion_thresh or
                scene_score > scene_thresh or
                frame_idx - last_selected >= (duration * fps / max_frames if duration > 0 else 30)  # Adaptive forced selection
            ):
                if frame_idx - last_selected >= min_gap:
                    selected_frames.append(frame)
                    last_selected = frame_idx

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
        cap.release()
    
    return selected_frames
