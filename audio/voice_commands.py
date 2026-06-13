import threading
from typing import Callable, Optional


class VoiceCommandDispatcher:
    def __init__(self):
        self._lock = threading.Lock()
        self._stop_callback: Optional[Callable[[], None]] = None

    def set_stop_callback(self, callback: Optional[Callable[[], None]]):
        with self._lock:
            self._stop_callback = callback

    def clear_stop_callback(self):
        self.set_stop_callback(None)

    def handle_text(self, text: str):
        if "stop" in text.lower().split():
            with self._lock:
                callback = self._stop_callback
            if callback:
                callback()
