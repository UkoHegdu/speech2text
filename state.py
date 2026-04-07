from enum import Enum, auto
from threading import Lock


class AppStatus(Enum):
    IDLE       = auto()
    RECORDING  = auto()
    PROCESSING = auto()


class AppState:
    """Thread-safe application state machine.

    Valid transitions:
        IDLE -> RECORDING  (hotkey #1)
        RECORDING -> PROCESSING  (hotkey #2)
        PROCESSING -> IDLE  (worker done or error)
    """

    _VALID = {
        AppStatus.IDLE:       {AppStatus.RECORDING},
        AppStatus.RECORDING:  {AppStatus.PROCESSING},
        AppStatus.PROCESSING: {AppStatus.IDLE},
    }

    def __init__(self) -> None:
        self._status = AppStatus.IDLE
        self._lock = Lock()

    @property
    def status(self) -> AppStatus:
        return self._status

    def transition_to(self, new_status: AppStatus) -> bool:
        """Attempt a state transition. Returns True on success, False if invalid."""
        with self._lock:
            if new_status in self._VALID.get(self._status, set()):
                self._status = new_status
                return True
            return False

    def is_idle(self) -> bool:
        return self._status is AppStatus.IDLE

    def is_recording(self) -> bool:
        return self._status is AppStatus.RECORDING

    def is_processing(self) -> bool:
        return self._status is AppStatus.PROCESSING
