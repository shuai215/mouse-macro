# mouse-macro

Mouse macro recorder and player — record mouse actions and keystrokes, replay them in loops.

Built with Python + PyQt6 + QFluentWidgets + pynput.

## Features

- Record mouse (move, click, scroll) and keyboard (except F1-F12)
- Replay with configurable loop count
- Global hotkeys work in-game (admin mode recommended)
- Keystroke recording: press Alt in-game to free the cursor, then click
- On-screen overlay notifications (recording/playback status, loop progress)

## Quick Start

Download `dist/mouse-macro.exe` and double-click to run. The app will ask whether to launch with admin rights — **choose Yes for game use**.

Or run from source:

```bash
conda activate mouse-macro
python -m mouse_macro.app
```

## Hotkeys

| Key | Action |
|-----|--------|
| **F6** | Start / Stop recording |
| **F7** | Start / Stop playback |
| **F7** (during playback) | Emergency stop (hardware-level, works in any game) |

## Usage

1. Launch the app (admin recommended)
2. Switch to the game
3. Press **F6** to start recording
4. Perform actions (move, click, press keys)
5. Press **F6** to stop (auto-saves to `data/autosave/`)
6. Press **F7** to replay

You can also use the UI buttons for recording/playback, save/load macro files, and switch language (Chinese/English).

## Dependencies

- Python 3.11+
- PyQt6
- PyQt6-Fluent-Widgets
- pynput

## Build

```bash
pyinstaller mouse-macro.spec
```

Output: `dist/mouse-macro.exe`

## Notes

- Admin rights are recommended for game use (some games intercept global hotkeys at lower privilege levels)
- F1-F12 keys are filtered from recording to prevent control key conflicts
- Mouse move events are compressed (recorded every ~5px instead of every pixel)
- Minimum delay between replayed actions is 8ms to ensure the game engine processes each input
