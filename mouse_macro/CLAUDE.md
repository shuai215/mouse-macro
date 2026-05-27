# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

鼠标宏录制与回放桌面应用 — 录制鼠标操作（移动、点击、滚轮），保存为 JSON，支持循环回放。

技术栈: Python 3 + PyQt6 + QFluentWidgets（UI 框架）+ pynput（鼠标/键盘钩子）

## 运行

```bash
python -m mouse_macro.app
```

未找到 requirements.txt / pyproject.toml。依赖项: `PyQt6`, `PyQt6-QFluentWidgets`, `pynput`

## 架构

三层结构，数据流单向：

```
ui/main_window.py          ← PyQt6 FluentWindow, 纯 UI + 信号连接
services/macro_controller.py ← 业务协调层, 持有 recorder/player/actions
core/                       ← 无 Qt 依赖的纯逻辑
```

- **`core/models.py`** — `MouseAction` 是 frozen dataclass，所有数据结构的唯一来源。新增字段时同步更新 `to_dict`/`from_dict`
- **`core/recorder.py`** — `MouseRecorder` 通过 pynput `mouse.Listener` 捕获事件，线程安全（Lock）。`_next_delay()` 基于 `time.perf_counter()` 记录动作间隔
- **`core/player.py`** — `MousePlayer` 在 daemon 线程中按 delay 回放，使用 `threading.Event` 实现可中断停止。`_execute()` 先移动位置再执行 click/scroll
- **`core/storage.py`** — JSON 序列化，纯函数，无状态
- **`core/hotkeys.py`** — `HotkeyManager` 封装 pynput `GlobalHotKeys`，F6 切换录制，F7 切换播放。回调在 pynput 线程中执行
- **`services/macro_controller.py`** — `MacroController` 协调层：管理状态互斥（录制中不能播放，播放中不能录制），autosave 每次停止录制自动写入 `data/autosave/latest_macro.json`
- **`ui/main_window.py`** — `MainWindow` 继承 `FluentWindow`，关键模式：hotkey 回调 → Qt signal → UI 线程 slot，确保线程安全。250ms 定时器轮询状态更新按钮启用/禁用

### 数据流

录制: pynput 事件 → `MouseRecorder._append()` (带 delay) → `MacroController.actions` → `save_actions()` → JSON
回放: `load_actions()` → `MacroController.actions` → `MousePlayer.play()` → daemon 线程逐条执行

### 文件布局

```
mouse_macro/
├── app.py                  # 入口: run() 创建 app/controller/window
├── core/
│   ├── models.py           # MouseAction dataclass
│   ├── recorder.py         # MouseRecorder
│   ├── player.py           # MousePlayer (threaded)
│   ├── storage.py          # JSON save/load
│   └── hotkeys.py          # F6/F7 全局热键
├── services/
│   └── macro_controller.py # 业务协调
└── ui/
    └── main_window.py      # Qt 主窗口
```
