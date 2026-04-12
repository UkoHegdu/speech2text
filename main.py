"""
Speech2Text — local speech-to-text with Whisper + Ollama cleanup.

Hotkey : Hold Ctrl+Win to record; release either key to stop.
Output : cleaned text pasted at cursor via Ctrl+V; also stored in clipboard
Quit   : right-click the system tray icon -> Quit
"""

import sys
import threading
import winsound
from typing import Optional

import config
import regex_cleaner
import vocab_manager
import window_tracker
from audio_recorder import AudioRecorder
from hotkey_listener import HotkeyListener
from llm_cleaner import LLMCleaner
from output_handler import OutputHandler
from state import AppState, AppStatus
from transcriber import Transcriber
from tray_icon import TrayIcon


class SpeechToTextApp:
    def __init__(self) -> None:
        self.state   = AppState()
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.cleaner  = LLMCleaner()
        self.output   = OutputHandler()
        self.tray     = TrayIcon(
            on_quit=self.shutdown,
            on_edit_vocab=self._edit_vocab,
            get_project_name=window_tracker.current_project,
        )
        self.hotkey   = HotkeyListener(on_start=self._start_recording, on_stop=self._stop_and_process)
        self._worker: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        self._startup_checks()
        window_tracker.start()
        print("[Speech2Text] Preloading Whisper model…")
        self.transcriber.preload()
        print("[Speech2Text] Ready.  Hotkey: Hold Ctrl+Win")

        self.hotkey.start()
        self.tray.start()   # Blocks main thread until Quit is clicked

    def shutdown(self) -> None:
        print("[Speech2Text] Shutting down.")
        self.hotkey.stop()
        if self.state.is_recording():
            self.recorder.stop()
        sys.exit(0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _start_recording(self) -> None:
        if not self.state.transition_to(AppStatus.RECORDING):
            return
        try:
            self.recorder.start()
        except Exception as exc:
            print(f"[Speech2Text] Microphone error: {exc}")
            self._beep(config.BEEP_ERROR)
            self.state.transition_to(AppStatus.IDLE)
            self.tray.update(AppStatus.IDLE)
            return

        self.tray.update(AppStatus.RECORDING)
        self._beep(config.BEEP_START)
        print("[Speech2Text] Recording…")

    def _stop_and_process(self) -> None:
        if not self.state.transition_to(AppStatus.PROCESSING):
            return
        self.tray.update(AppStatus.PROCESSING)
        self._beep(config.BEEP_STOP)
        print("[Speech2Text] Processing…")

        self._worker = threading.Thread(target=self._worker_fn, daemon=True)
        self._worker.start()

    def _worker_fn(self) -> None:
        try:
            audio = self.recorder.stop()
            if audio is None:
                print("[Speech2Text] No audio captured — too short or silent.")
                self._beep(config.BEEP_ERROR)
                return

            # Transcribe — inject vocab for the current project
            project = window_tracker.current_project()
            terms = vocab_manager.load_terms(project)
            if terms:
                print(f"[Speech2Text] Vocab ({project or 'global'}): {terms}")
            print("[Speech2Text] Transcribing…")
            raw = self.transcriber.transcribe(audio, vocab_terms=terms or None)
            if not raw.strip():
                print("[Speech2Text] Nothing recognised.")
                self._beep(config.BEEP_ERROR)
                return
            print(f"[Speech2Text] Raw      : {raw}")

            # Regex pass — fast, always available
            if config.REGEX_CLEAN_ENABLED:
                cleaned = regex_cleaner.clean(raw)
                print(f"[Speech2Text] Regex    : {cleaned}")
            else:
                cleaned = raw

            # LLM pass — optional second pass via Ollama
            if config.LLM_ENABLED:
                print("[Speech2Text] Cleaning with Ollama…")
                cleaned = self.cleaner.clean(cleaned)
                print(f"[Speech2Text] LLM      : {cleaned}")

            # Deliver
            self.output.deliver(cleaned)
            self._beep(config.BEEP_DONE)
            print("[Speech2Text] Pasted ✓")

        except Exception as exc:
            print(f"[Speech2Text] Error: {exc}")
            self._beep(config.BEEP_ERROR)

        finally:
            self.state.transition_to(AppStatus.IDLE)
            self.tray.update(AppStatus.IDLE)

    # ------------------------------------------------------------------

    def _edit_vocab(self, project: str) -> None:
        vocab_manager.open_for_editing(project)

    def _startup_checks(self) -> None:
        if config.LLM_ENABLED:
            if self.cleaner.is_available():
                print(f"[Speech2Text] Ollama OK — model: {config.OLLAMA_MODEL}")
            else:
                print(
                    "[Speech2Text] WARNING: Ollama not reachable at "
                    f"{config.OLLAMA_BASE_URL}. LLM cleanup disabled."
                )
                config.LLM_ENABLED = False

    @staticmethod
    def _beep(params: tuple) -> None:
        try:
            winsound.Beep(*params)
        except Exception:
            pass   # No audio device — silently skip


# ----------------------------------------------------------------------

def main() -> None:
    app = SpeechToTextApp()
    app.run()


if __name__ == "__main__":
    main()
