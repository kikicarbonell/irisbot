"""database.py — Async CRUD functions using `aiosqlite`.

Kept simple and async-first to comply with project requirements.
"""

import json
import logging
from typing import Dict, Optional

import aiosqlite

from config import DB_PATH

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


async def init_db() -> None:
    """Initialize DB and create necessary tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH.as_posix()) as db:
        await db.execute(CREATE_UNITS_TABLE)
        await db.commit()


async def insert_unit(data: Dict) -> None:
    """Insert or replace a unit in the `units` table.

    `data` should contain at least `url` and an `id` or it will be derived from the URL.
    """
    unit_id = data.get("id") or data.get("url")
    metadata = json.dumps(
        {k: v for k, v in data.items() if k not in ("id", "url", "title", "price_raw")}
    )
    async with aiosqlite.connect(DB_PATH.as_posix()) as db:
        try:
            await db.execute(
                """INSERT OR REPLACE INTO units (id, url, title, price_raw, metadata)
                VALUES (?, ?, ?, ?, ?)""",
                (unit_id, data.get("url"), data.get("title"), data.get("price_raw"), metadata),
            )
            await db.commit()
        except Exception as exc:
            logger.exception("Error inserting unit %s: %s", unit_id, exc)


async def fetch_unit(unit_id: str) -> Optional[Dict]:
    """Retrieve a unit by ID from the database.

    Args:
        unit_id: The unique identifier of the unit to fetch.

    Returns:
        Dictionary with unit data (id, url, title, price_raw, metadata) or None if not found.
    """
    async with aiosqlite.connect(DB_PATH.as_posix()) as db:
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
