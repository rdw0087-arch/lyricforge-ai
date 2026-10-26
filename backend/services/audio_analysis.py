from __future__ import annotations

import os
from typing import Any, Dict

import numpy as np

try:
    import librosa
except ImportError:  # pragma: no cover
    librosa = None

try:
    import whisper
except ImportError:  # pragma: no cover
    whisper = None


class AudioAnalysisError(Exception):
    pass


def ensure_audio_dependencies() -> None:
    missing = []
    if librosa is None:
        missing.append("librosa")
    if whisper is None:
        missing.append("whisper")

    if missing:
        raise AudioAnalysisError(
            "Missing audio dependencies: " + ", ".join(missing) + ". Install with: pip install librosa whisper"
        )


def analyze_audio_file(audio_path: str) -> Dict[str, Any]:
    if not os.path.exists(audio_path):
        raise AudioAnalysisError(f"Audio file not found: {audio_path}")

    ensure_audio_dependencies()

    y, sr = librosa.load(audio_path, sr=None, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    duration_seconds = len(y) / sr

    model = whisper.load_model("base")
    transcript_result = model.transcribe(audio_path, fp16=False)

    return {
        "tempo_bpm": float(tempo),
        "sample_rate": int(sr),
        "duration_seconds": float(duration_seconds),
        "energy_curve": rms.tolist(),
        "beats": beats.tolist(),
        "lyric_transcript": transcript_result.get("text", ""),
        "lyric_segments": transcript_result.get("segments", []),
    }
