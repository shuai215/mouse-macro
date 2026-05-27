from __future__ import annotations

from PyQt6.QtCore import QPoint, QTimer, Qt
from PyQt6.QtWidgets import QApplication, QLabel


class NotificationOverlay(QLabel):
    """A borderless always-on-top label for brief or persistent notifications."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet(
            "QLabel {"
            "  color: #fff;"
            "  background: rgba(0,0,0,200);"
            "  padding: 12px 24px;"
            "  border-radius: 8px;"
            "  font-size: 16px;"
            "  font-weight: bold;"
            "}"
        )
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def _center(self) -> None:
        self.adjustSize()
        screen = QApplication.primaryScreen()
        if screen is not None:
            self.move(QPoint(20, 20))

    def notify(self, text: str, duration_ms: int = 1500) -> None:
        """Show briefly then auto-dismiss."""
        self._timer.stop()
        self.setText(text)
        self._center()
        self._timer.start(duration_ms)
        self.show()

    def show_persistent(self, text: str) -> None:
        """Show persistently until hide() is called."""
        self._timer.stop()
        self.setText(text)
        self._center()
        self.show()
