import time

import pyperclip
from pynput.keyboard import Controller as KeyboardController, Key


class OutputHandler:
    def __init__(self) -> None:
        self._keyboard = KeyboardController()

    def send_to_clipboard(self, text: str) -> None:
        pyperclip.copy(text)

    def paste_at_cursor(self) -> None:
        """Simulate Ctrl+V. Always safe to call — worst case nothing is focused."""
        time.sleep(0.05)   # Let clipboard write settle (Win32 clipboard is async)
        self._keyboard.press(Key.ctrl)
        time.sleep(0.02)
        self._keyboard.press("v")
        time.sleep(0.02)
        self._keyboard.release("v")
        time.sleep(0.02)
        self._keyboard.release(Key.ctrl)

    def deliver(self, text: str) -> None:
        """Copy to clipboard then paste. Text is always in clipboard as a fallback."""
        self.send_to_clipboard(text)
        self.paste_at_cursor()
