"""db_manager.py — Encapsulates database logic.

Separates init, insert, and fetch in a testable class with db_path injection.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import aiosqlite

logger = logging.getLogger(__name__)


CREATE_UNITS_TABLE = """
CREATE TABLE IF NOT EXISTS units (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    price_raw TEXT,
    metadata TEXT,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


class DBManager:
    """Database manager for unit table operations.

    Encapsulates all database CRUD operations with error handling and logging.
    """

    def __init__(self, db_path: Path):
        """Initialize the database manager.

        Args:
            db_path: Path object pointing to the SQLite database file.
        """
        self.db_path = db_path

    async def init(self) -> None:
        """Initialize DB and create necessary tables."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path.as_posix()) as db:
            await db.execute(CREATE_UNITS_TABLE)
            await db.commit()

    async def insert_unit(self, data: Dict[str, Any]) -> None:
        """Insert or replace a unit in the `units` table.

        `data` should contain at least `url` and an `id` or it will be derived from the URL.
        """
        unit_id = data.get("id") or data.get("url")
        metadata = json.dumps(
            {k: v for k, v in data.items() if k not in ("id", "url", "title", "price_raw")}
        )
        async with aiosqlite.connect(self.db_path.as_posix()) as db:
            try:
                await db.execute(
                    """INSERT OR REPLACE INTO units (id, url, title, price_raw, metadata)
                    VALUES (?, ?, ?, ?, ?)""",
                    (unit_id, data.get("url"), data.get("title"), data.get("price_raw"), metadata),
                )
                await db.commit()
            except Exception as exc:
                logger.exception("Error inserting unit %s: %s", unit_id, exc)

    async def fetch_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """Get a unit by id; returns None if it doesn't exist."""
        async with aiosqlite.connect(self.db_path.as_posix()) as db:
            async with db.execute(
                "SELECT id, url, title, price_raw, metadata FROM units WHERE id = ?", (unit_id,)
            ) as cur:
                row = await cur.fetchone()
                if not row:
                    return None
                id_, url, title, price_raw, metadata = row
                try:
                    meta = json.loads(metadata or "{}")
                except Exception:
                    meta = {"raw_metadata": metadata}
                return {"id": id_, "url": url, "title": title, "price_raw": price_raw, **meta}
