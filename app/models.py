from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class CardRecord:
    card_id: int
    name: str
    desc: str
    ot: int
    alias: int
    setcode: int
    type_value: int
    atk: int
    defense: int
    level: int
    race: int
    attribute: int
    category: int
    extra_texts: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AppSettings:
    cdb_path: str = ""
    secondary_cdb_path: str = ""
    pics_path: str = ""
    template_path: str = ""
    output_path: str = ""
    language: str = "zh_TW"


@dataclass(slots=True)
class CardContext:
    card: CardRecord
    local_image_path: Path | None
    public_image_url: str
    comment: str
