"""
Manages per-project and global vocabulary files used to bias Whisper transcription.

File layout:
  ~/.speech2text/vocab/_global.txt          — always loaded
  ~/.speech2text/vocab/<projectname>.txt    — loaded when that project is active

Format: one term per line; lines starting with # are comments.
"""
import os
from pathlib import Path

VOCAB_DIR = Path.home() / ".speech2text" / "vocab"

_TEMPLATE = """\
# Vocabulary for {name}
# One term per line. Lines starting with # are ignored.
# Example:
# Kalman filter
# pyproject.toml
"""


def _read_file(path: Path) -> list[str]:
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def load_terms(project: str) -> list[str]:
    """Return combined global + project-specific vocabulary terms."""
    terms = []
    for filename in ("_global.txt", f"{project}.txt") if project else ("_global.txt",):
        path = VOCAB_DIR / filename
        if path.exists():
            terms.extend(_read_file(path))
    return terms


def open_for_editing(project: str) -> None:
    """Create the vocab file for *project* if needed, then open it in Notepad."""
    VOCAB_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{project}.txt" if project else "_global.txt"
    path = VOCAB_DIR / filename
    if not path.exists():
        path.write_text(_TEMPLATE.format(name=project or "global"), encoding="utf-8")
    os.startfile(str(path))
