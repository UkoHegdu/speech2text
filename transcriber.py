from typing import Optional

import numpy as np

import config


class Transcriber:
    """Wraps faster-whisper. Model is loaded lazily on first transcription."""

    def __init__(self) -> None:
        self._model = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        from faster_whisper import WhisperModel
        print(f"[Transcriber] Loading Whisper '{config.WHISPER_MODEL_SIZE}' model…")
        self._model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
        print("[Transcriber] Model ready.")

    def preload(self) -> None:
        """Call at startup so the first transcription isn't slow."""
        self._ensure_loaded()

    def transcribe(self, audio: np.ndarray, vocab_terms: list[str] | None = None) -> str:
        """Return a transcript string from a float32 audio array.

        vocab_terms: domain-specific words/phrases appended to the initial
        prompt so Whisper biases toward their spelling (e.g. 'Kalman filter').
        """
        self._ensure_loaded()
        prompt = config.WHISPER_INITIAL_PROMPT
        if vocab_terms:
            prompt += " " + ", ".join(vocab_terms) + "."
        segments, _ = self._model.transcribe(
            audio,
            beam_size=5,
            language=config.WHISPER_LANGUAGE,
            vad_filter=config.WHISPER_VAD_FILTER,
            initial_prompt=prompt,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
