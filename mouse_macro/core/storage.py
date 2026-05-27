from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from mouse_macro.core.models import MouseAction


def save_actions(path: str | Path, actions: Iterable[MouseAction]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = [action.to_dict() for action in actions]
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_actions(path: str | Path) -> list[MouseAction]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Macro file must contain a list of mouse actions.")
    return [MouseAction.from_dict(item) for item in payload]
