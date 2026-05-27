from __future__ import annotations

import ctypes
import threading
import time
from collections.abc import Callable, Sequence

from pynput import keyboard, mouse

from mouse_macro.core.models import MouseAction

VK_F7 = 0x76
MIN_DELAY = 0.008


class MousePlayer:
    def __init__(self) -> None:
        self._mouse = mouse.Controller()
        self._keyboard = keyboard.Controller()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_playing(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def play(
        self,
        actions: Sequence[MouseAction],
        loop_count: int = 1,
        on_loop: Callable[[int, int], None] | None = None,
    ) -> None:
        if self.is_playing:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            args=(list(actions), max(1, loop_count), on_loop),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    @staticmethod
    def _is_f7_pressed() -> bool:
        return ctypes.windll.user32.GetAsyncKeyState(VK_F7) & 0x8000 != 0

    @staticmethod
    def _drain_f7() -> None:
        while MousePlayer._is_f7_pressed():
            time.sleep(0.05)

    def _run(
        self,
        actions: list[MouseAction],
        loop_count: int,
        on_loop: Callable[[int, int], None] | None,
    ) -> None:
        self._drain_f7()

        for loop_idx in range(loop_count):
            if on_loop:
                on_loop(loop_idx + 1, loop_count)
            for action in actions:
                if self._stop_event.is_set() or self._is_f7_pressed():
                    return
                time.sleep(max(action.delay, MIN_DELAY))
                self._execute(action)

    def _execute(self, action: MouseAction) -> None:
        if action.action_type == "key" and action.button:
            key = self._resolve_key(action.button)
            if key is not None:
                if action.pressed:
                    self._keyboard.press(key)
                else:
                    self._keyboard.release(key)
            return

        if action.x is not None and action.y is not None:
            self._mouse.position = (action.x, action.y)

        if action.action_type == "click" and action.button:
            button = getattr(mouse.Button, action.button)
            if action.pressed:
                self._mouse.press(button)
            else:
                self._mouse.release(button)
        elif action.action_type == "scroll":
            self._mouse.scroll(action.dx or 0, action.dy or 0)

    @staticmethod
    def _resolve_key(name: str) -> keyboard.Key | keyboard.KeyCode | None:
        try:
            return getattr(keyboard.Key, name)
        except AttributeError:
            pass
        if len(name) == 1:
            return keyboard.KeyCode.from_char(name)
        return None
