from __future__ import annotations

import threading
import time
from collections.abc import Sequence

from pynput import mouse

from mouse_macro.core.models import MouseAction


class MousePlayer:
    def __init__(self) -> None:
        self._controller = mouse.Controller()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_playing(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def play(self, actions: Sequence[MouseAction], loop_count: int = 1) -> None:
        if self.is_playing:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            args=(list(actions), max(1, loop_count)),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self, actions: list[MouseAction], loop_count: int) -> None:
        for _ in range(loop_count):
            for action in actions:
                if self._stop_event.is_set():
                    return
                time.sleep(action.delay)
                self._execute(action)

    def _execute(self, action: MouseAction) -> None:
        if action.x is not None and action.y is not None:
            self._controller.position = (action.x, action.y)

        if action.action_type == "click" and action.button:
            button = getattr(mouse.Button, action.button)
            if action.pressed:
                self._controller.press(button)
            else:
                self._controller.release(button)
        elif action.action_type == "scroll":
            self._controller.scroll(action.dx or 0, action.dy or 0)
