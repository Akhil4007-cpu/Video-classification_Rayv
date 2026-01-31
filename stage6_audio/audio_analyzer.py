from faster_whisper import WhisperModel

_whisper_model = None

RISK_WORDS = {
    "kill", "beat", "hit", "die",
    "blood", "knife", "gun",
    "threat", "abuse", "fight",
    "stab", "murder"
}

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="float32"
        )
    return _whisper_model


def analyze_audio(audio_path):
    model = get_whisper_model()
    segments, _ = model.transcribe(audio_path)

    risk_hits = 0

    for seg in segments:
        text = seg.text.lower()
        for word in RISK_WORDS:
            if word in text:
                risk_hits += 1

    if risk_hits == 0:
        score = 0.0
    elif risk_hits == 1:
        score = 0.3
    elif risk_hits == 2:
        score = 0.6
    else:
        score = 0.9

    return {"risk_score": score}

