import cv2
import numpy as np

def smart_sample(
    video_path,
    motion_thresh=30,  # Higher threshold for more selective sampling
    scene_thresh=45,  # Higher threshold
    min_gap=10,        # Larger gap between frames (was 5)
    max_frames=4       # Fewer frames total (was 10)
):
    cap = cv2.VideoCapture(video_path)

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

            # More selective criteria for important frames only
            if (
                motion_score > motion_thresh or
                scene_score > scene_thresh or
                frame_idx - last_selected >= 40  # Less frequent forced selection
            ):
                if frame_idx - last_selected >= min_gap:
                    selected_frames.append(frame)
                    last_selected = frame_idx

        prev_gray = gray
        frame_idx += 1

        if len(selected_frames) >= max_frames:
            break

    cap.release()
    return selected_frames
