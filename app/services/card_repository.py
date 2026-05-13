from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
import shutil

from app.models import CardRecord


TEXT_COLUMNS = [f"str{i}" for i in range(1, 17)]


class CardRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        self._cards: list[CardRecord] = []

    def load(self) -> list[CardRecord]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            text_column_sql = ",\n                ".join(f"texts.{column}" for column in TEXT_COLUMNS)
            query = f"""
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
                texts.desc,
                {text_column_sql}
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
                        extra_texts=[row[column] or "" for column in TEXT_COLUMNS],
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

    def get_card_by_id(self, card_id: int) -> CardRecord | None:
        for card in self._cards:
            if card.card_id == card_id:
                return card
        return None

    def create_backup(self) -> Path:
        database_path = Path(self.database_path)
        backup_dir = database_path.parent / "cdb_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{database_path.stem}_{timestamp}{database_path.suffix}"
        shutil.copy2(database_path, backup_path)
        return backup_path

    def _normalize_extra_texts(self, extra_texts: list[str]) -> list[str]:
        return (extra_texts + [""] * len(TEXT_COLUMNS))[: len(TEXT_COLUMNS)]

    def add_card(self, card: CardRecord) -> Path:
        backup_path = self.create_backup()
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute("BEGIN")
            exists = connection.execute("SELECT 1 FROM datas WHERE id = ?", (card.card_id,)).fetchone()
            if exists is not None:
                raise ValueError("此卡號已存在，無法新增。")

            connection.execute(
                """
                INSERT INTO datas (id, ot, alias, setcode, type, atk, def, level, race, attribute, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card.card_id,
                    card.ot,
                    card.alias,
                    card.setcode,
                    card.type_value,
                    card.atk,
                    card.defense,
                    card.level,
                    card.race,
                    card.attribute,
                    card.category,
                ),
            )

            placeholders = ", ".join(["?"] * (3 + len(TEXT_COLUMNS)))
            column_sql = ", ".join(["id", "name", "desc", *TEXT_COLUMNS])
            connection.execute(
                f"INSERT INTO texts ({column_sql}) VALUES ({placeholders})",
                (
                    card.card_id,
                    card.name,
                    card.desc,
                    *self._normalize_extra_texts(card.extra_texts),
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return backup_path

    def update_card(self, original_id: int, card: CardRecord) -> Path:
        backup_path = self.create_backup()
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute("BEGIN")

            if original_id != card.card_id:
                exists = connection.execute("SELECT 1 FROM datas WHERE id = ?", (card.card_id,)).fetchone()
                if exists is not None:
                    raise ValueError("新的卡號已存在，無法覆蓋。")

            datas_cursor = connection.execute(
                """
                UPDATE datas
                SET
                    id = ?,
                    ot = ?,
                    alias = ?,
                    setcode = ?,
                    type = ?,
                    atk = ?,
                    def = ?,
                    level = ?,
                    race = ?,
                    attribute = ?,
                    category = ?
                WHERE id = ?
                """,
                (
                    card.card_id,
                    card.ot,
                    card.alias,
                    card.setcode,
                    card.type_value,
                    card.atk,
                    card.defense,
                    card.level,
                    card.race,
                    card.attribute,
                    card.category,
                    original_id,
                ),
            )

            text_assignments = ", ".join(f"{column} = ?" for column in TEXT_COLUMNS)
            texts_cursor = connection.execute(
                f"""
                UPDATE texts
                SET
                    id = ?,
                    name = ?,
                    desc = ?,
                    {text_assignments}
                WHERE id = ?
                """,
                (
                    card.card_id,
                    card.name,
                    card.desc,
                    *self._normalize_extra_texts(card.extra_texts),
                    original_id,
                ),
            )

            if datas_cursor.rowcount != 1 or texts_cursor.rowcount != 1:
                raise ValueError("找不到要更新的卡片資料。")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return backup_path

    def delete_card(self, card_id: int) -> Path:
        backup_path = self.create_backup()
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute("BEGIN")
            connection.execute("DELETE FROM texts WHERE id = ?", (card_id,))
            cursor = connection.execute("DELETE FROM datas WHERE id = ?", (card_id,))
            if cursor.rowcount != 1:
                raise ValueError("找不到要刪除的卡片資料。")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return backup_path

    def upsert_cards(self, cards: list[CardRecord]) -> Path:
        if not cards:
            raise ValueError("No cards selected.")

        backup_path = self.create_backup()
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute("BEGIN")
            for card in cards:
                exists = connection.execute("SELECT 1 FROM datas WHERE id = ?", (card.card_id,)).fetchone()
                if exists is None:
                    connection.execute(
                        """
                        INSERT INTO datas (id, ot, alias, setcode, type, atk, def, level, race, attribute, category)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            card.card_id,
                            card.ot,
                            card.alias,
                            card.setcode,
                            card.type_value,
                            card.atk,
                            card.defense,
                            card.level,
                            card.race,
                            card.attribute,
                            card.category,
                        ),
                    )
                    placeholders = ", ".join(["?"] * (3 + len(TEXT_COLUMNS)))
                    column_sql = ", ".join(["id", "name", "desc", *TEXT_COLUMNS])
                    connection.execute(
                        f"INSERT INTO texts ({column_sql}) VALUES ({placeholders})",
                        (
                            card.card_id,
                            card.name,
                            card.desc,
                            *self._normalize_extra_texts(card.extra_texts),
                        ),
                    )
                    continue

                connection.execute(
                    """
                    UPDATE datas
                    SET
                        ot = ?,
                        alias = ?,
                        setcode = ?,
                        type = ?,
                        atk = ?,
                        def = ?,
                        level = ?,
                        race = ?,
                        attribute = ?,
                        category = ?
                    WHERE id = ?
                    """,
                    (
                        card.ot,
                        card.alias,
                        card.setcode,
                        card.type_value,
                        card.atk,
                        card.defense,
                        card.level,
                        card.race,
                        card.attribute,
                        card.category,
                        card.card_id,
                    ),
                )
                text_assignments = ", ".join(f"{column} = ?" for column in TEXT_COLUMNS)
                connection.execute(
                    f"""
                    UPDATE texts
                    SET
                        name = ?,
                        desc = ?,
                        {text_assignments}
                    WHERE id = ?
                    """,
                    (
                        card.name,
                        card.desc,
                        *self._normalize_extra_texts(card.extra_texts),
                        card.card_id,
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return backup_path
