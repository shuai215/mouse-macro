from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MouseAction:
    action_type: str
    delay: float
    x: int | None = None
    y: int | None = None
    button: str | None = None
    pressed: bool | None = None
    dx: int | None = None
    dy: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MouseAction":
        return cls(
            action_type=str(data["action_type"]),
            delay=float(data["delay"]),
            x=data.get("x"),
            y=data.get("y"),
            button=data.get("button"),
            pressed=data.get("pressed"),
            dx=data.get("dx"),
            dy=data.get("dy"),
        )
