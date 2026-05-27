# Development Log

## 2026-05-27

- Created a dedicated conda environment for the mouse macro project.
- Environment name: `mouse-macro`
- Python version: `3.11.15`
- Environment path: `D:\python\envs\mouse-macro`
- Verification command: `conda run -n mouse-macro python --version`
- Result: Python started successfully and reported `Python 3.11.15`.

Next TODO:
- Install runtime dependencies: `PyQt6`, `PyQt6-Fluent-Widgets`, and `pynput`.
- Scaffold the MVP project structure.

## 2026-05-27

- Installed runtime dependencies into the `mouse-macro` conda environment.
- Packages installed:
  - `PyQt6`
  - `PyQt6-Fluent-Widgets`
  - `pynput`
- Verification command: `conda run -n mouse-macro python -c "from PyQt6.QtWidgets import QApplication; import qfluentwidgets; import pynput; print('imports ok')"`
- Result: imports completed successfully.

Next TODO:
- Scaffold the PyQt6 + QFluentWidgets MVP project structure.
- Implement the core data model, recorder, player, storage, hotkeys, and main window.

## 2026-05-27

- Scaffolded the first MVP code structure for the mouse macro app.
- Added core modules:
  - `mouse_macro/core/models.py` for `MouseAction`
  - `mouse_macro/core/storage.py` for JSON save/load
  - `mouse_macro/core/recorder.py` for mouse event recording
  - `mouse_macro/core/player.py` for mouse playback
  - `mouse_macro/core/hotkeys.py` for global `F6`/`F7` hotkeys
- Added service layer:
  - `mouse_macro/services/macro_controller.py`
- Added UI layer:
  - `mouse_macro/ui/main_window.py`
  - `mouse_macro/app.py`
  - `main.py`
- Added `requirements.txt` and initial tests in `tests/test_models_storage.py`.
- UI decisions:
  - `F6` toggles recording.
  - `F7` toggles playback.
  - stopping a recording automatically saves a draft to `data/autosave/latest_macro.json`.
  - manual save writes a chosen formal macro file.
  - global hotkey callbacks are bridged into the Qt UI thread through signals.
- Verification commands:
  - `D:\python\envs\mouse-macro\python.exe -m pytest tests`
  - `D:\python\envs\mouse-macro\python.exe -m compileall mouse_macro main.py`
  - PyQt offscreen window smoke test
- Results:
  - `2 passed`
  - compile check succeeded
  - window smoke test printed `window smoke ok`

Risks / TODO:
- Real mouse recording and playback still need manual testing in a normal desktop session.
- Mouse move events are currently recorded at full frequency; later we should add sampling or compression.
- The first UI is functional but still minimal.

## 2026-05-27

- Investigated packaged executable failure:
  - Error: `ImportError: DLL load failed while importing QtWidgets`.
  - Source environment import worked, so the issue was isolated to PyInstaller packaging.
  - Found two `.spec` files and two `dist/build` outputs.
  - The stale child spec had no PyQt6 binaries or datas.
  - The root spec contained hard-coded project paths that were corrupted by Chinese path encoding.
- Rebuilt the root `mouse-macro.spec`:
  - Uses `SPECPATH` instead of hard-coded project paths.
  - Explicitly collects PyQt6 dynamic libraries.
  - Explicitly collects Qt platform/style/icon/image plugins and translations.
  - Explicitly collects QFluentWidgets data and hidden imports.
  - Disables UPX for a safer Qt bundle.
- Rebuilt with:
  - `D:\python\envs\mouse-macro\python.exe -m PyInstaller mouse-macro.spec --noconfirm`
- Verification:
  - `D:\python\envs\mouse-macro\python.exe -m pytest tests` -> `5 passed`
  - `D:\python\envs\mouse-macro\python.exe -m compileall mouse_macro main.py` -> succeeded
  - Ran `D:\鼠标宏\dist\mouse-macro.exe` smoke test -> exited without the QtWidgets import traceback.

Risks / TODO:
- `mouse_macro\mouse-macro.spec` and `mouse_macro\dist` are stale packaging artifacts; do not use them.
- Manual GUI testing is still needed because the smoke test only checks that the packaged app starts far enough to avoid the QtWidgets DLL import failure.

## 2026-05-27

- Investigated continued packaged startup failure from screenshot:
  - Error still occurred at `from PyQt6.QtWidgets import QApplication`.
  - The admin permission prompt was not the direct failing line, but Qt was imported before `_ensure_admin()` could run.
- Changed `mouse_macro/app.py`:
  - Fixed the garbled Chinese admin prompt text.
  - Moved PyQt6 and UI imports inside `run()` after `_ensure_admin()`.
- Changed `mouse-macro.spec`:
  - Switched packaging from onefile to onedir for Qt reliability.
  - New executable path: `dist\mouse-macro\mouse-macro.exe`.
  - Qt files verified in output:
    - `dist\mouse-macro\_internal\PyQt6\Qt6\bin\Qt6Widgets.dll`
    - `dist\mouse-macro\_internal\PyQt6\Qt6\plugins\platforms\qwindows.dll`
- Rebuilt with:
  - `D:\python\envs\mouse-macro\python.exe -m PyInstaller mouse-macro.spec --noconfirm`
- Verification:
  - Ran `dist\mouse-macro\mouse-macro.exe` smoke test -> no QtWidgets traceback observed.
  - `D:\python\envs\mouse-macro\python.exe -m pytest tests` -> `5 passed`.
  - `D:\python\envs\mouse-macro\python.exe -m compileall mouse_macro main.py` -> succeeded.

Risks / TODO:
- The root `dist\mouse-macro.exe` is now only the onedir launcher stub; use `dist\mouse-macro\mouse-macro.exe` as the packaged app.
- If distributing the app, zip the whole `dist\mouse-macro` folder, not just the exe.

## 2026-05-27

- Temporarily disabled admin elevation in `mouse_macro/app.py`.
- Reason:
  - In source mode, `sys.executable` points to `D:\python\envs\mouse-macro\python.exe`.
  - The elevation relaunch started Python without passing `main.py`, which opened an interactive Python console instead of the app.
- Verification:
  - `D:\python\envs\mouse-macro\python.exe -m pytest tests` -> `5 passed`
  - `D:\python\envs\mouse-macro\python.exe -m compileall mouse_macro main.py` -> succeeded
- TODO:
  - Re-implement elevation later with separate handling for source mode and PyInstaller frozen mode.

## 2026-05-27

- User confirmed packaged startup works after disabling admin elevation.
- Conclusion:
  - Current PyInstaller onedir packaging is usable.
  - The previous startup failure was caused by the admin relaunch logic, not by the base app startup path.
- Decision:
  - Keep admin elevation disabled for now while stabilizing the MVP.
  - Re-add elevation later as an optional feature with separate source-mode and frozen-exe code paths.

## 2026-05-27

- Cleaned unused generated artifacts after confirming the correct onedir package path.
- Deleted:
  - `.pytest_cache`
  - `__pycache__`
  - `build`
  - `dist\mouse-macro.exe`
  - `mouse_macro\build`
  - `mouse_macro\dist`
  - `mouse_macro\mouse-macro.spec`
- Kept:
  - source package `mouse_macro`
  - entry point `main.py`
  - correct root spec `mouse-macro.spec`
  - correct packaged app folder `dist\mouse-macro`
- Verification:
  - confirmed `mouse_macro\app.py`, `main.py`, `mouse-macro.spec`, and `dist\mouse-macro\mouse-macro.exe` still exist.
  - confirmed packaged Qt files still exist:
    - `dist\mouse-macro\_internal\PyQt6\Qt6\bin\Qt6Widgets.dll`
    - `dist\mouse-macro\_internal\PyQt6\Qt6\plugins\platforms\qwindows.dll`
