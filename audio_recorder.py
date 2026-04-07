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

    def stop(self) -> Optional[np.ndarray]:
        """Stop recording and return the captured audio as a flat float32 array.

        Returns None if nothing was captured or the recording was too short.
        """
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if not self._frames:
            return None

        audio = np.concatenate(self._frames, axis=0).flatten()
        min_samples = int(config.SAMPLE_RATE * config.MIN_RECORDING_SECONDS)
        return audio if len(audio) >= min_samples else None

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
