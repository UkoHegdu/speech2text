"""
Tracks the active VS Code project by scanning all open windows.

Strategy:
  1. Prefer the last window that was in the foreground (most recently worked on).
  2. Fall back to any visible VS Code window if none was ever foregrounded.

VS Code title formats:
  "filename — project — Visual Studio Code"
  "project — Visual Studio Code"
"""
import ctypes
import ctypes.wintypes
import threading
import time

_VSCODE_SUFFIX = " - Visual Studio Code"
_lock = threading.Lock()
_last_foreground_project: str = ""   # VS Code project last seen as foreground

_EnumWindowsProc = ctypes.WINFUNCTYPE(
    ctypes.c_bool,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LPARAM,
)


def _extract_project(title: str) -> str | None:
    if not title.endswith(_VSCODE_SUFFIX):
        return None
    inner = title[: -len(_VSCODE_SUFFIX)]
    return inner.split(" - ")[-1].strip() or None


def _scan_all_windows() -> str:
    """Return the project name from any visible VS Code window, or ''."""
    user32 = ctypes.windll.user32
    buf = ctypes.create_unicode_buffer(512)
    found: list[str] = []

    def _cb(hwnd: int, _: int) -> bool:
        if user32.IsWindowVisible(hwnd):
            user32.GetWindowTextW(hwnd, buf, 512)
            project = _extract_project(buf.value)
            if project:
                found.append(project)
        return True

    user32.EnumWindows(_EnumWindowsProc(_cb), 0)
    return found[0] if found else ""


def _poll() -> None:
    global _last_foreground_project
    user32 = ctypes.windll.user32
    buf = ctypes.create_unicode_buffer(512)
    while True:
        user32.GetWindowTextW(user32.GetForegroundWindow(), buf, 512)
        project = _extract_project(buf.value)
        if project:
            with _lock:
                _last_foreground_project = project
        time.sleep(1)


def start() -> None:
    """Start the background polling thread (daemon — exits with the app)."""
    threading.Thread(target=_poll, daemon=True).start()


def current_project() -> str:
    """Return the most relevant VS Code project name, or '' if VS Code isn't open."""
    with _lock:
        if _last_foreground_project:
            return _last_foreground_project
    # Fallback: scan all windows right now
    return _scan_all_windows()
