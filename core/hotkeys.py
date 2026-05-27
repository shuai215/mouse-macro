from __future__ import annotations

from collections.abc import Callable

from pynput import keyboard


class HotkeyManager:
    def __init__(
        self,
        on_record_toggle: Callable[[], None],
        on_play_toggle: Callable[[], None],
    ) -> None:
        self._listener = keyboard.GlobalHotKeys(
            {
                "<f6>": on_record_toggle,
                "<f7>": on_play_toggle,
            }
        )

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()
