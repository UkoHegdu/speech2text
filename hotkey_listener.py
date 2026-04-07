import threading
from typing import Callable, Optional

from pynput import keyboard
from pynput.keyboard import Key


class HotkeyListener:
    """Hold Ctrl+Win to record; release either key to stop.

    Uses a raw keyboard.Listener with manual modifier tracking so the
    combination works system-wide on Windows.
    """

    def __init__(
        self,
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
    ) -> None:
        self._on_start = on_start
        self._on_stop  = on_stop
        self._pressed: set = set()
        self._active   = False          # True while we're in a recording hold
        self._listener: Optional[keyboard.Listener] = None

    def start(self) -> None:
        """Start the listener in a daemon thread."""
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()

    # ------------------------------------------------------------------

    def _is_ctrl(self) -> bool:
        return bool(self._pressed & {Key.ctrl, Key.ctrl_l, Key.ctrl_r})

    def _is_win(self) -> bool:
        return bool(self._pressed & {Key.cmd, Key.cmd_l, Key.cmd_r})

    def _on_press(self, key: Key) -> None:
        self._pressed.add(key)
        if not self._active and self._is_ctrl() and self._is_win():
            self._active = True
            threading.Thread(target=self._on_start, daemon=True).start()

    def _on_release(self, key: Key) -> None:
        self._pressed.discard(key)
        if self._active and (not self._is_ctrl() or not self._is_win()):
            self._active = False
            threading.Thread(target=self._on_stop, daemon=True).start()
