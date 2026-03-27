from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


ToolHandler = Callable[[dict], dict]


@dataclass(slots=True)
class Tool:
    name: str
    handler: ToolHandler

    def run(self, payload: dict) -> dict:
        return self.handler(payload)
