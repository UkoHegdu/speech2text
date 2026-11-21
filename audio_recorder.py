from typing import Optional

import numpy as np
import sounddevice as sd

import config


class AudioRecorder:
    def __init__(self) -> None:
        self._frames: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None

    def start(self) -> None:
        """Open the default microphone and begin buffering audio."""
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            dtype=config.DTYPE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return the captured audio as a flat float32 array.

        Returns an empty array if no frames arrived at all (e.g. a dead USB
        mic never fired its callback), distinct from a short-but-real clip.
        """
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if not self._frames:
            return np.array([], dtype=config.DTYPE)

        return np.concatenate(self._frames, axis=0).flatten()

    def is_silent(self, audio: np.ndarray) -> bool:
        """True if the captured audio is near-zero throughout, or empty.

        Catches the case where the input stream is open and buffering frames
        but the device itself delivered nothing (e.g. a USB mic that went
        dead after the hub it's attached to suspended/resumed) — including
        when no callback fired at all, i.e. a fully dead mic.
        """
        if audio.size == 0:
            return True
        return float(np.sqrt(np.mean(np.square(audio)))) < config.SILENCE_RMS_THRESHOLD

    def is_too_short(self, audio: np.ndarray) -> bool:
        """True if real (non-silent) audio was captured but below the minimum length."""
        min_samples = int(config.SAMPLE_RATE * config.MIN_RECORDING_SECONDS)
        return len(audio) < min_samples

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time: object,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            print(f"[Recorder] {status}")
        self._frames.append(indata.copy())
