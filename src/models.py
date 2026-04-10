from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Document:
    id: str
    content: str
    metadata: dict[str, any] = field(default_factory=dict)
