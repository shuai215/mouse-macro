from pathlib import Path

from pynput.keyboard import Key, KeyCode

from mouse_macro.core.models import MouseAction
from mouse_macro.core.recorder import MouseRecorder
from mouse_macro.core.storage import load_actions, save_actions


def test_mouse_action_round_trips_through_dict() -> None:
    action = MouseAction(
        action_type="click",
        delay=0.125,
        x=320,
        y=240,
        button="left",
        pressed=True,
    )

    restored = MouseAction.from_dict(action.to_dict())

    assert restored == action


def test_storage_saves_and_loads_actions(tmp_path: Path) -> None:
    actions = [
        MouseAction(action_type="move", delay=0.01, x=100, y=200),
        MouseAction(action_type="scroll", delay=0.03, x=100, y=200, dx=0, dy=-1),
    ]
    path = tmp_path / "macro.json"

    save_actions(path, actions)
    loaded = load_actions(path)

    assert loaded == actions


def test_recorder_skips_small_moves() -> None:
    recorder = MouseRecorder(min_move_distance=5)
    recorder._on_move(100, 100)
    recorder._on_move(102, 101)  # dx=2, dy=1 -> max=2 < 5, skip
    recorder._on_move(103, 102)  # dx=3, dy=2 -> max=3 < 5, skip
    recorder._on_move(104, 103)  # dx=4, dy=3 -> max=4 < 5, skip
    recorder._on_move(101, 105)  # dx=1, dy=5 -> max=5 >= 5, record

    assert len(recorder._actions) == 2
    a1 = recorder._actions[0]
    a2 = recorder._actions[1]
    assert a1.action_type == "move" and a1.x == 100 and a1.y == 100
    assert a2.action_type == "move" and a2.x == 101 and a2.y == 105


def test_recorder_skips_f_keys() -> None:
    recorder = MouseRecorder()
    recorder._on_key_press(Key.f6)
    recorder._on_key_release(Key.f6)
    recorder._on_key_press(Key.f12)
    recorder._on_key_release(Key.f12)

    assert recorder.actions() == []


def test_recorder_captures_normal_keys() -> None:
    recorder = MouseRecorder()
    recorder._on_key_press(Key.alt_l)
    recorder._on_key_release(Key.alt_l)
    recorder._on_key_press(KeyCode.from_char("a"))
    recorder._on_key_release(KeyCode.from_char("a"))

    assert len(recorder._actions) == 4
    actions = recorder._actions
    assert actions[0] == MouseAction("key", actions[0].delay, button="alt_l", pressed=True)
    assert actions[1] == MouseAction("key", actions[1].delay, button="alt_l", pressed=False)
    assert actions[2] == MouseAction("key", actions[2].delay, button="a", pressed=True)
    assert actions[3] == MouseAction("key", actions[3].delay, button="a", pressed=False)
