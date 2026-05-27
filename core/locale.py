from __future__ import annotations

from enum import Enum
from collections.abc import Callable


class Language(Enum):
    EN = "en"
    ZH = "zh"


TRANSLATIONS: dict[str, dict[str, str]] = {
    # window
    "window_title":        {"en": "Mouse Macro", "zh": "鼠标宏"},
    "page_title":          {"en": "Mouse Macro MVP", "zh": "鼠标宏 MVP"},
    # status
    "status_idle":         {"en": "Idle", "zh": "空闲"},
    "status_recording":    {"en": "Recording", "zh": "录制中"},
    "status_playing":      {"en": "Playing", "zh": "回放中"},
    # buttons
    "btn_record":          {"en": "Record  F6", "zh": "开始录制  F6"},
    "btn_stop_record":     {"en": "Stop Record  F6", "zh": "停止录制  F6"},
    "btn_play":            {"en": "Play  F7", "zh": "播放  F7"},
    "btn_stop_play":       {"en": "Stop Play  F7", "zh": "停止播放  F7"},
    "btn_save":            {"en": "Save As  Ctrl+S", "zh": "保存为  Ctrl+S"},
    "btn_load":            {"en": "Load  Ctrl+O", "zh": "加载  Ctrl+O"},
    "btn_lang_en":         {"en": "中文", "zh": "English"},
    # labels
    "label_actions":       {"en": "Actions: {}", "zh": "动作数: {}"},
    "label_file":          {"en": "File: {}", "zh": "文件: {}"},
    "label_loop":          {"en": "Repeat", "zh": "循环次数"},
    "label_language":      {"en": "Language", "zh": "语言"},
    # file dialogs
    "dialog_save_title":   {"en": "Save Macro", "zh": "保存宏"},
    "dialog_load_title":   {"en": "Load Macro", "zh": "加载宏"},
    # info messages
    "info_record_stopped": {"en": "Recording stopped", "zh": "录制已停止"},
    "info_autosaved":      {"en": "Draft saved, actions: {}", "zh": "已自动保存草稿，动作数: {}"},
    "info_saved":          {"en": "Saved", "zh": "已保存"},
    "info_loaded":         {"en": "Loaded", "zh": "已加载"},
}


class LocaleManager:
    def __init__(self, language: Language = Language.ZH) -> None:
        self._language = language
        self._listeners: list[Callable[[], None]] = []

    @property
    def language(self) -> Language:
        return self._language

    def set_language(self, language: Language) -> None:
        if language == self._language:
            return
        self._language = language
        for cb in self._listeners:
            cb()

    def tr(self, key: str, *args: object) -> str:
        text = TRANSLATIONS.get(key, {}).get(self._language.value, key)
        if args:
            text = text.format(*args)
        return text

    def on_change(self, callback: Callable[[], None]) -> None:
        self._listeners.append(callback)
