from __future__ import annotations

from pathlib import Path

from mouse_macro.core.models import MouseAction
from mouse_macro.core.player import MousePlayer
from mouse_macro.core.recorder import MouseRecorder
from mouse_macro.core.storage import load_actions, save_actions


class MacroController:
    def __init__(self, autosave_path: str | Path) -> None:
        self.autosave_path = Path(autosave_path)
        self.recorder = MouseRecorder()
        self.player = MousePlayer()
        self.actions: list[MouseAction] = []
        self.current_path: Path | None = None

    @property
    def is_recording(self) -> bool:
        return self.recorder.is_recording

    @property
    def is_playing(self) -> bool:
        return self.player.is_playing

    def start_recording(self) -> None:
        if self.is_playing:
            self.stop_playing()
        self.recorder.start()

    def stop_recording(self) -> int:
        self.actions = self.recorder.stop()
        save_actions(self.autosave_path, self.actions)
        self.current_path = self.autosave_path
        return len(self.actions)

    def toggle_recording(self) -> int | None:
        if self.is_recording:
            return self.stop_recording()
        self.start_recording()
        return None

    def play(self, loop_count: int = 1) -> None:
        if not self.actions:
            return
        if self.is_recording:
            self.stop_recording()
        self.player.play(self.actions, loop_count)

    def stop_playing(self) -> None:
        self.player.stop()

    def toggle_playing(self, loop_count: int = 1) -> None:
        if self.is_playing:
            self.stop_playing()
        else:
            self.play(loop_count)

    def save_as(self, path: str | Path) -> None:
        save_actions(path, self.actions)
        self.current_path = Path(path)

    def load(self, path: str | Path) -> int:
        self.actions = load_actions(path)
        self.current_path = Path(path)
        return len(self.actions)
