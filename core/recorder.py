from __future__ import annotations

import time
from threading import Lock

from pynput import mouse

from mouse_macro.core.models import MouseAction


class MouseRecorder:
    def __init__(self) -> None:
        self._actions: list[MouseAction] = []
        self._listener: mouse.Listener | None = None
        self._last_time: float | None = None
        self._lock = Lock()

    @property
    def is_recording(self) -> bool:
        return self._listener is not None

    def start(self) -> None:
        if self.is_recording:
            return
        with self._lock:
            self._actions.clear()
            self._last_time = time.perf_counter()
        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._listener.start()

    def stop(self) -> list[MouseAction]:
        listener = self._listener
        self._listener = None
        if listener is not None:
            listener.stop()
        return self.actions()

    def actions(self) -> list[MouseAction]:
        with self._lock:
            return list(self._actions)

    def _next_delay(self) -> float:
        now = time.perf_counter()
        previous = self._last_time if self._last_time is not None else now
        self._last_time = now
        return max(0.0, now - previous)

    def _append(self, action: MouseAction) -> None:
        with self._lock:
            self._actions.append(action)

    def _on_move(self, x: int, y: int) -> None:
        self._append(MouseAction("move", self._next_delay(), x=x, y=y))

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        self._append(
            MouseAction(
                "click",
                self._next_delay(),
                x=x,
                y=y,
                button=button.name,
                pressed=pressed,
            )
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        self._append(
            MouseAction("scroll", self._next_delay(), x=x, y=y, dx=dx, dy=dy)
        )
