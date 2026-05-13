from __future__ import annotations

from pathlib import Path


class ImageIndexer:
    SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self._index: dict[str, Path] = {}

    def build(self) -> dict[str, Path]:
        index: dict[str, Path] = {}
        if self.base_dir.exists():
            for path in self.base_dir.iterdir():
                if path.is_file() and path.suffix.lower() in self.SUPPORTED_SUFFIXES:
                    index[path.stem] = path.resolve()
        self._index = index
        return index

    def get(self, card_id: int) -> Path | None:
        return self._index.get(str(card_id))
