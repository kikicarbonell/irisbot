"""db_manager.py — Encapsula la lógica de base de datos.

Separa init, insert y fetch en una clase testeable con inyección de db_path.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

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
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def init(self) -> None:
        """Inicializa la DB y crea tablas necesarias."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path.as_posix()) as db:
            await db.execute(CREATE_UNITS_TABLE)
            await db.commit()

    async def insert_unit(self, data: Dict[str, Any]) -> None:
        """Inserta o reemplaza una unidad en la tabla `units`.

        `data` debería contener al menos `url` y un `id` o se derivará del URL.
        """
        unit_id = data.get("id") or data.get("url")
        metadata = json.dumps({k: v for k, v in data.items() if k not in ("id", "url", "title", "price_raw")})
        async with aiosqlite.connect(self.db_path.as_posix()) as db:
            try:
                await db.execute(
                    """INSERT OR REPLACE INTO units (id, url, title, price_raw, metadata)
                    VALUES (?, ?, ?, ?, ?)""",
                    (unit_id, data.get("url"), data.get("title"), data.get("price_raw"), metadata),
                )
                await db.commit()
            except Exception as exc:
                logger.exception("Error insertando unidad %s: %s", unit_id, exc)

    async def fetch_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una unidad por id; retorna None si no existe."""
        async with aiosqlite.connect(self.db_path.as_posix()) as db:
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
