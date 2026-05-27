from __future__ import annotations

import time
from threading import Lock

from pynput import keyboard, mouse

from mouse_macro.core.models import MouseAction

_SKIP_KEYS = frozenset({
    keyboard.Key.f1, keyboard.Key.f2, keyboard.Key.f3, keyboard.Key.f4,
    keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8,
    keyboard.Key.f9, keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12,
})


class MouseRecorder:
    def __init__(self, min_move_distance: int = 5) -> None:
        self._actions: list[MouseAction] = []
        self._listener: mouse.Listener | None = None
        self._kb_listener: keyboard.Listener | None = None
        self._last_time: float | None = None
        self._last_recorded_pos: tuple[int, int] | None = None
        self._min_move_distance = min_move_distance
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
            self._last_recorded_pos = None
        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._listener.start()
        self._kb_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._kb_listener.start()

    def stop(self) -> list[MouseAction]:
        listener = self._listener
        kb_listener = self._kb_listener
        self._listener = None
        self._kb_listener = None
        if listener is not None:
            listener.stop()
        if kb_listener is not None:
            kb_listener.stop()
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
        prev = self._last_recorded_pos
        if prev is not None:
            if max(abs(x - prev[0]), abs(y - prev[1])) < self._min_move_distance:
                return
        self._last_recorded_pos = (x, y)
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

    def _on_key_press(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        if key is None or key in _SKIP_KEYS:
            return
        name = self._key_name(key)
        self._append(MouseAction("key", self._next_delay(), button=name, pressed=True))

    def _on_key_release(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        if key is None or key in _SKIP_KEYS:
            return
        name = self._key_name(key)
        self._append(MouseAction("key", self._next_delay(), button=name, pressed=False))

    @staticmethod
    def _key_name(key: keyboard.Key | keyboard.KeyCode) -> str:
        if isinstance(key, keyboard.KeyCode):
            return key.char if key.char is not None else key.name
        return key.name
