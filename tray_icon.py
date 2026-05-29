from typing import Callable, Optional

from PIL import Image, ImageDraw
import pystray

import config
import startup_manager
from state import AppStatus


_COLORS = {
    AppStatus.IDLE:       (46, 204, 113),   # green
    AppStatus.RECORDING:  (231, 76,  60),   # red
    AppStatus.PROCESSING: (241, 196, 15),   # yellow
}

_TITLES = {
    AppStatus.IDLE:       "Speech2Text — Ready",
    AppStatus.RECORDING:  "Speech2Text — Recording…",
    AppStatus.PROCESSING: "Speech2Text — Processing…",
}


def _make_image(status: AppStatus = AppStatus.IDLE) -> Image.Image:
    color = _COLORS.get(status, _COLORS[AppStatus.IDLE])
    sz = 64
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Background circle
    d.ellipse([2, 2, sz - 2, sz - 2], fill=color)

    # Mic capsule
    d.rectangle([24, 14, 40, 34], fill="white")
    d.ellipse([24, 10, 40, 28], fill="white")

    # Mic stand arc
    d.arc([18, 26, 46, 46], start=0, end=180, fill="white", width=3)

    # Vertical stem + base
    d.line([32, 46, 32, 54], fill="white", width=3)
    d.line([25, 54, 39, 54], fill="white", width=3)

    return img


class TrayIcon:
    def __init__(
        self,
        on_quit: Callable[[], None],
        on_edit_vocab: Callable[[str], None],
        get_project_name: Callable[[], str],
        on_toggle_vad: Callable[[], None],
    ) -> None:
        self._on_quit = on_quit
        self._on_edit_vocab = on_edit_vocab
        self._get_project_name = get_project_name
        self._on_toggle_vad = on_toggle_vad
        self._icon: Optional[pystray.Icon] = None
        self._last_known_project: str = ""

    def _vocab_label(self, item: pystray.MenuItem) -> str:
        project = self._get_project_name()
        self._last_known_project = project  # snapshot while editor is still last foreground
        if project:
            return f"Edit vocabulary for '{project}'"
        return "Edit vocabulary (focus VS Code or Claude first)"

    def start(self) -> None:
        """Blocking — must be called from the main thread on Windows."""
        menu = pystray.Menu(
            pystray.MenuItem(self._vocab_label, self._edit_vocab_clicked),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "VAD filter (skip silence)",
                self._vad_clicked,
                checked=lambda item: config.WHISPER_VAD_FILTER,
            ),
            pystray.MenuItem(
                "Start with Windows",
                self._startup_clicked,
                checked=lambda item: startup_manager.is_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit_clicked),
        )
        self._icon = pystray.Icon(
            "speech2text",
            _make_image(AppStatus.IDLE),
            _TITLES[AppStatus.IDLE],
            menu,
        )
        self._icon.run()   # blocks until icon.stop() is called

    def update(self, status: AppStatus) -> None:
        """Thread-safe icon + tooltip update."""
        if self._icon:
            self._icon.icon  = _make_image(status)
            self._icon.title = _TITLES.get(status, "Speech2Text")

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()

    def _edit_vocab_clicked(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._on_edit_vocab(self._last_known_project)

    def _vad_clicked(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._on_toggle_vad()

    def _startup_clicked(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        startup_manager.toggle()

    def _quit_clicked(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        icon.stop()
        self._on_quit()
