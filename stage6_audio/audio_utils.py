import subprocess
import os

FFMPEG_PATH = r"C:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"


def extract_audio(video_path, output_path="temp_audio.wav"):
    if not os.path.exists(FFMPEG_PATH):
        return None

    cmd = [
        FFMPEG_PATH, "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", "16000", output_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
        return output_path
    except subprocess.CalledProcessError:
        return None
