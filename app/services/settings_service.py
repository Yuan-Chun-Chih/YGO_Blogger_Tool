from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.models import AppSettings


class SettingsService:
    def __init__(self, settings_path: str | Path) -> None:
        self.settings_path = Path(settings_path)

    def load(self) -> AppSettings:
        if not self.settings_path.exists():
            return AppSettings()

        data = json.loads(self.settings_path.read_text(encoding="utf-8"))
        return AppSettings(**data)

    def save(self, settings: AppSettings) -> None:
        self.settings_path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
