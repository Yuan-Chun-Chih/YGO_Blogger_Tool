from __future__ import annotations

import sqlite3
from pathlib import Path

from app.models import CardRecord


class CardRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        self._cards: list[CardRecord] = []

    def load(self) -> list[CardRecord]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            query = """
            SELECT
                datas.id,
                datas.ot,
                datas.alias,
                datas.setcode,
                datas.type,
                datas.atk,
                datas.def,
                datas.level,
                datas.race,
                datas.attribute,
                datas.category,
                texts.name,
                texts.desc
            FROM datas
            INNER JOIN texts ON texts.id = datas.id
            ORDER BY texts.name COLLATE NOCASE
            """
            cards: list[CardRecord] = []
            for row in connection.execute(query):
                cards.append(
                    CardRecord(
                        card_id=row["id"],
                        name=row["name"] or "",
                        desc=row["desc"] or "",
                        ot=row["ot"] or 0,
                        alias=row["alias"] or 0,
                        setcode=row["setcode"] or 0,
                        type_value=row["type"] or 0,
                        atk=row["atk"] if row["atk"] is not None else -1,
                        defense=row["def"] if row["def"] is not None else -1,
                        level=row["level"] or 0,
                        race=row["race"] or 0,
                        attribute=row["attribute"] or 0,
                        category=row["category"] or 0,
                    )
                )
        finally:
            connection.close()

        self._cards = cards
        return cards

    @property
    def cards(self) -> list[CardRecord]:
        return self._cards

    def search(self, keyword: str) -> list[CardRecord]:
        normalized = keyword.strip().lower()
        if not normalized:
            return self._cards

        return [
            card
            for card in self._cards
            if normalized in card.name.lower() or normalized in str(card.card_id)
        ]
