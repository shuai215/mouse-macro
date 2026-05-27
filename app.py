from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from mouse_macro.core.locale import LocaleManager
from mouse_macro.services.macro_controller import MacroController
from mouse_macro.ui.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    locale = LocaleManager()
    controller = MacroController(Path("data/autosave/latest_macro.json"))
    window = MainWindow(controller, locale)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
