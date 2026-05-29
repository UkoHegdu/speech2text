"""
Tracks the active editor project via foreground-window polling.

Supported editors:
  VS Code  — title ends with " - Visual Studio Code"
  Claude   — foreground process is claude.exe (title is usually "Claude")

Two callsites, two functions:
  current_project() — strict: non-empty only when a supported editor is the
                      foreground window right now.  Used at recording time so
                      vocab is never applied when the user is in another app.
  last_project()    — returns the most recently seen project, up to
                      EDITOR_TIMEOUT_SECS after the editor was last in focus.
                      Used for the "Edit vocabulary" tray label (the editor may
                      have lost focus when the tray is opened).

VS Code title formats:
  "filename — project — Visual Studio Code"
  "project — Visual Studio Code"
"""
import ctypes
import ctypes.wintypes
import threading
import time
from pathlib import Path

import config

_VSCODE_SUFFIX = " - Visual Studio Code"
_CLAUDE_TITLE_SUFFIX = " - Claude"

# After this many seconds without a supported editor in the foreground, the
# cached project name is cleared.
EDITOR_TIMEOUT_SECS = 5 * 60   # 5 minutes

_lock = threading.Lock()
_last_foreground_project: str = ""
_last_editor_focus_time: float = 0.0   # monotonic timestamp of last editor focus


def _extract_vscode_project(title: str) -> str | None:
    if not title.endswith(_VSCODE_SUFFIX):
        return None
    inner = title[: -len(_VSCODE_SUFFIX)]
    return inner.split(" - ")[-1].strip() or None


def _extract_claude_project(title: str) -> str:
    if title.endswith(_CLAUDE_TITLE_SUFFIX):
        inner = title[: -len(_CLAUDE_TITLE_SUFFIX)].strip()
        if inner:
            return inner
    return config.CLAUDE_VOCAB_PROJECT


def _foreground_hwnd() -> int:
    return ctypes.windll.user32.GetForegroundWindow()


def _foreground_title() -> str:
    user32 = ctypes.windll.user32
    buf = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(_foreground_hwnd(), buf, 512)
    return buf.value


def _foreground_process_name() -> str:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    hwnd = _foreground_hwnd()
    if not hwnd:
        return ""
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(32768)
        size = ctypes.wintypes.DWORD(len(buf))
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return ""
        return Path(buf.value).name.lower()
    finally:
        kernel32.CloseHandle(handle)


def _extract_project(title: str, process_name: str) -> str | None:
    vscode = _extract_vscode_project(title)
    if vscode:
        return vscode
    if process_name == config.CLAUDE_PROCESS_NAME.lower():
        return _extract_claude_project(title)
    return None


def _poll() -> None:
    global _last_foreground_project, _last_editor_focus_time
    while True:
        title = _foreground_title()
        process_name = _foreground_process_name()
        project = _extract_project(title, process_name)
        now = time.monotonic()
        with _lock:
            if project:
                _last_foreground_project = project
                _last_editor_focus_time = now
            elif _last_foreground_project and (
                now - _last_editor_focus_time > EDITOR_TIMEOUT_SECS
            ):
                print(
                    f"[WindowTracker] Editor inactive for {EDITOR_TIMEOUT_SECS}s"
                    f" — clearing cached project '{_last_foreground_project}'."
                )
                _last_foreground_project = ""
                _last_editor_focus_time = 0.0
        time.sleep(1)


def start() -> None:
    """Start the background polling thread (daemon — exits with the app)."""
    threading.Thread(target=_poll, daemon=True).start()


def current_project() -> str:
    """Return the project only if a supported editor is the foreground window.

    Returns '' when any other app is in focus — vocab is then skipped for that
    recording.
    """
    title = _foreground_title()
    process_name = _foreground_process_name()
    return _extract_project(title, process_name) or ""


def last_project() -> str:
    """Return the most recently seen project (within EDITOR_TIMEOUT_SECS).

    Safe to call when the editor has temporarily lost focus (e.g. tray click).
    Returns '' if no supported editor project was seen recently.
    """
    with _lock:
        return _last_foreground_project
