from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    FluentWindow,
    InfoBar,
    InfoBarPosition,
    NavigationItemPosition,
    PrimaryPushButton,
    PushButton,
    SpinBox,
    StrongBodyLabel,
)
from qfluentwidgets.components.navigation import NavigationPushButton

from mouse_macro.core.hotkeys import HotkeyManager
from mouse_macro.core.locale import Language, LocaleManager
from mouse_macro.services.macro_controller import MacroController


class _UiSignals(QObject):
    record_hotkey = pyqtSignal()
    play_hotkey = pyqtSignal()


class MainWindow(FluentWindow):
    def __init__(self, controller: MacroController, locale: LocaleManager) -> None:
        super().__init__()
        self.controller = controller
        self.locale = locale
        self.signals = _UiSignals()
        self.hotkeys = HotkeyManager(
            on_record_toggle=self._on_record_hotkey,
            on_play_toggle=self._on_play_hotkey,
        )
        self.state_timer = QTimer(self)
        self.state_timer.setInterval(250)

        self._setup_window()
        self._create_widgets()
        self._build_ui()
        self._connect_signals()
        self._update_state()
        self.hotkeys.start()
        self.state_timer.start()
        self.locale.on_change(self._refresh_ui)

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.hotkeys.stop()
        self.controller.stop_playing()
        if self.controller.is_recording:
            self.controller.stop_recording()
        super().closeEvent(event)

    def _setup_window(self) -> None:
        self.setWindowTitle(self.locale.tr("window_title"))
        self.resize(760, 460)

    def _create_widgets(self) -> None:
        self.status_label = StrongBodyLabel()
        self.count_label = BodyLabel()
        self.path_label = BodyLabel()
        self.loop_spin = SpinBox()
        self.loop_spin.setRange(1, 999)
        self.loop_spin.setValue(1)

        self.record_button = PrimaryPushButton()
        self.stop_record_button = PushButton()
        self.play_button = PrimaryPushButton()
        self.stop_play_button = PushButton()
        self.save_button = PushButton()
        self.load_button = PushButton()
        self.lang_toggle_btn = NavigationPushButton(FluentIcon.LANGUAGE, "", False)

    def _build_ui(self) -> None:
        page = QWidget()
        page.setObjectName("macroPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = StrongBodyLabel(self.locale.tr("page_title"))
        layout.addWidget(title)
        layout.addWidget(self.status_label)
        layout.addWidget(self.count_label)
        layout.addWidget(self.path_label)

        record_row = QHBoxLayout()
        record_row.addWidget(self.record_button)
        record_row.addWidget(self.stop_record_button)
        layout.addLayout(record_row)

        play_row = QHBoxLayout()
        play_row.addWidget(self.play_button)
        play_row.addWidget(self.stop_play_button)
        play_row.addWidget(QLabel(self.locale.tr("label_loop")))
        play_row.addWidget(self.loop_spin)
        layout.addLayout(play_row)

        file_row = QHBoxLayout()
        file_row.addWidget(self.save_button)
        file_row.addWidget(self.load_button)
        layout.addLayout(file_row)

        layout.addStretch(1)
        self.addSubInterface(page, FluentIcon.HOME, "Macro")

        self.navigationInterface.addWidget(
            "langToggle",
            self.lang_toggle_btn,
            position=NavigationItemPosition.BOTTOM,
        )
        self._refresh_lang_btn()
        self._refresh_labels()

    def _refresh_lang_btn(self) -> None:
        self.lang_toggle_btn.setToolTip(self.locale.tr("btn_lang_en"))

    def _connect_signals(self) -> None:
        self.record_button.clicked.connect(self.start_recording)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.play_button.clicked.connect(self.play)
        self.stop_play_button.clicked.connect(self.stop_playing)
        self.save_button.clicked.connect(self.save_as)
        self.load_button.clicked.connect(self.load_macro)
        self.lang_toggle_btn.clicked.connect(self._on_lang_toggle)
        self.signals.record_hotkey.connect(self._toggle_recording_from_ui_thread)
        self.signals.play_hotkey.connect(self._toggle_playing_from_ui_thread)
        self.state_timer.timeout.connect(self._update_state)

    def start_recording(self) -> None:
        self.controller.start_recording()
        self._update_state()

    def stop_recording(self) -> None:
        count = self.controller.stop_recording()
        self._show_info(
            self.locale.tr("info_record_stopped"),
            self.locale.tr("info_autosaved", count),
        )
        self._update_state()

    def play(self) -> None:
        self.controller.play(self.loop_spin.value())
        self._update_state()

    def stop_playing(self) -> None:
        self.controller.stop_playing()
        self._update_state()

    def save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.locale.tr("dialog_save_title"),
            str(Path("data/macros/macro.json")),
            "JSON Files (*.json)",
        )
        if not path:
            return
        self.controller.save_as(path)
        self._show_info(self.locale.tr("info_saved"), path)
        self._update_state()

    def load_macro(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.locale.tr("dialog_load_title"),
            str(Path("data/macros")),
            "JSON Files (*.json)",
        )
        if not path:
            return
        count = self.controller.load(path)
        self._show_info(
            self.locale.tr("info_loaded"),
            f"{path}, {self.locale.tr('label_actions', count)}",
        )
        self._update_state()

    def _on_record_hotkey(self) -> None:
        self.signals.record_hotkey.emit()

    def _on_play_hotkey(self) -> None:
        self.signals.play_hotkey.emit()

    def _on_lang_toggle(self) -> None:
        if self.locale.language == Language.ZH:
            self.locale.set_language(Language.EN)
        else:
            self.locale.set_language(Language.ZH)

    def _toggle_recording_from_ui_thread(self) -> None:
        count = self.controller.toggle_recording()
        if count is not None:
            self._show_info(
                self.locale.tr("info_record_stopped"),
                self.locale.tr("info_autosaved", count),
            )
        self._update_state()

    def _toggle_playing_from_ui_thread(self) -> None:
        self.controller.toggle_playing(self.loop_spin.value())
        self._update_state()

    def _refresh_ui(self) -> None:
        self._setup_window()
        self._refresh_labels()
        self._refresh_lang_btn()
        self._update_state()

    def _refresh_labels(self) -> None:
        self.record_button.setText(self.locale.tr("btn_record"))
        self.stop_record_button.setText(self.locale.tr("btn_stop_record"))
        self.play_button.setText(self.locale.tr("btn_play"))
        self.stop_play_button.setText(self.locale.tr("btn_stop_play"))
        self.save_button.setText(self.locale.tr("btn_save"))
        self.load_button.setText(self.locale.tr("btn_load"))

    def _update_state(self) -> None:
        if self.controller.is_recording:
            status = self.locale.tr("status_recording")
        elif self.controller.is_playing:
            status = self.locale.tr("status_playing")
        else:
            status = self.locale.tr("status_idle")

        self.status_label.setText(status)
        self.count_label.setText(
            self.locale.tr("label_actions", len(self.controller.actions))
        )
        path = self.controller.current_path or self.controller.autosave_path
        self.path_label.setText(self.locale.tr("label_file", path))

        is_idle = (status == self.locale.tr("status_idle"))
        has_actions = bool(self.controller.actions)
        self.record_button.setEnabled(is_idle)
        self.stop_record_button.setEnabled(status == self.locale.tr("status_recording"))
        self.play_button.setEnabled(is_idle and has_actions)
        self.stop_play_button.setEnabled(status == self.locale.tr("status_playing"))
        self.save_button.setEnabled(is_idle and has_actions)
        self.load_button.setEnabled(is_idle)

    def _show_info(self, title: str, content: str) -> None:
        InfoBar.success(
            title=title,
            content=content,
            orient="horizontal",
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2500,
            parent=self,
        )
