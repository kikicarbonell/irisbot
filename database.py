"""database.py — funciones CRUD asíncronas usando `aiosqlite`.

Se mantiene simple y async-first para cumplir las reglas del proyecto.
"""

from pathlib import Path
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
    """Inicializa la DB y crea tablas necesarias."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH.as_posix()) as db:
        await db.execute(CREATE_UNITS_TABLE)
        await db.commit()


async def insert_unit(data: Dict) -> None:
    """Inserta o reemplaza una unidad en la tabla `units`.

    `data` debería contener al menos `url` y un `id` o se derivará del URL.
    """
    unit_id = data.get("id") or data.get("url")
    metadata = json.dumps({k: v for k, v in data.items() if k not in ("id", "url", "title", "price_raw")})
    async with aiosqlite.connect(DB_PATH.as_posix()) as db:
        try:
            await db.execute(
                """INSERT OR REPLACE INTO units (id, url, title, price_raw, metadata)
                VALUES (?, ?, ?, ?, ?)""",
                (unit_id, data.get("url"), data.get("title"), data.get("price_raw"), metadata),
            )
            await db.commit()
        except Exception as exc:
            logger.exception("Error insertando unidad %s: %s", unit_id, exc)


async def fetch_unit(unit_id: str) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH.as_posix()) as db:
        async with db.execute("SELECT id, url, title, price_raw, metadata FROM units WHERE id = ?", (unit_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            id_, url, title, price_raw, metadata = row
            try:
                meta = json.loads(metadata or "{}")
            except Exception:
                meta = {"raw_metadata": metadata}
            return {"id": id_, "url": url, "title": title, "price_raw": price_raw, **meta}
