from __future__ import annotations

from collections.abc import Callable

from pynput import keyboard


class HotkeyManager:
    def __init__(
        self,
        on_record_toggle: Callable[[], None],
        on_play_toggle: Callable[[], None],
    ) -> None:
        self._on_record_toggle = on_record_toggle
        self._on_play_toggle = on_play_toggle
        self._listener = keyboard.Listener(on_press=self._on_press)

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        if key == keyboard.Key.f6:
            self._on_record_toggle()
        elif key == keyboard.Key.f7:
            self._on_play_toggle()
