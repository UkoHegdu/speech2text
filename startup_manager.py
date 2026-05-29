import sys
import winreg
from pathlib import Path

_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "Speech2Text"


def _startup_command() -> str:
    python = Path(sys.executable)
    pythonw = python.parent / "pythonw.exe"
    if not pythonw.exists():
        pythonw = python
    script = (Path(__file__).resolve().parent / "main.py").resolve()
    return f'"{pythonw}" "{script}"'


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as key:
            winreg.QueryValueEx(key, _APP_NAME)
            return True
    except FileNotFoundError:
        return False


def enable() -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, access=winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, _startup_command())


def disable() -> None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, access=winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, _APP_NAME)
    except FileNotFoundError:
        pass


def toggle() -> bool:
    """Toggle startup state. Returns the new state (True = enabled)."""
    if is_enabled():
        disable()
        return False
    else:
        enable()
        return True
