from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path


def _is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _runtime_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent / "_internal"))
    return Path(__file__).resolve().parents[1]


def _configure_dll_search_path() -> None:
    runtime_dir = _runtime_dir()
    candidate_dirs = [
        runtime_dir,
        runtime_dir / "PyQt6" / "Qt6" / "bin",
        runtime_dir / "PyQt6" / "Qt6" / "plugins" / "platforms",
    ]

    existing_dirs = [path for path in candidate_dirs if path.exists()]
    for path in existing_dirs:
        try:
            os.add_dll_directory(str(path))
        except (AttributeError, OSError):
            pass

    current_path = os.environ.get("PATH", "")
    os.environ["PATH"] = os.pathsep.join(
        [str(path) for path in existing_dirs] + [current_path]
    )


def _request_admin() -> None:
    """Re-launch the current executable or script with admin privileges."""
    params = subprocess.list2cmdline(sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        params,
        str(Path(sys.executable).parent),
        1,
    )


def _ensure_admin() -> None:
    if _is_admin():
        return
    result = ctypes.windll.user32.MessageBoxW(
        0,
        "是否需要以管理员权限启动？\n(游戏环境下建议使用管理员权限)\n\n"
        "Run as Administrator? (recommended for games)",
        "Mouse Macro",
        0x00000004 | 0x00000020,  # Yes/No + Question icon
    )
    if result == 6:  # IDYES
        _request_admin()
        sys.exit(0)


def run() -> int:
    # Temporarily disabled while debugging packaged startup.
    # _ensure_admin()
    _configure_dll_search_path()

    from PyQt6.QtWidgets import QApplication

    from mouse_macro.core.locale import LocaleManager
    from mouse_macro.services.macro_controller import MacroController
    from mouse_macro.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    locale = LocaleManager()
    controller = MacroController(Path("data/autosave/latest_macro.json"))
    window = MainWindow(controller, locale)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
