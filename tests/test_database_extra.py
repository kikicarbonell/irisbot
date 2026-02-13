import importlib
import asyncio
from typing import Any

import pytest


@pytest.mark.asyncio
async def test_insert_handles_execute_exception(monkeypatch, tmp_path):
    # Ensure DB_PATH points to tmp so init_db won't fail
    monkeypatch.setenv("BASE_DIR", str(tmp_path))
    import config as cfg
    importlib.reload(cfg)

    import database as db
    importlib.reload(db)

    class DummyDB:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def execute(self, *args, **kwargs):
            raise Exception("execute failed")

        async def commit(self):
            pass

    async def fake_connect(*args, **kwargs) -> Any:
        return DummyDB()

    monkeypatch.setattr(db, "aiosqlite", type("M", (), {"connect": lambda *a, **k: DummyDB()}))

    sample = {"url": "http://example.com/u/err", "title": "Err Unit", "price_raw": "$0"}
    # Should not raise despite execute raising (insert_unit catches and logs)
    await db.insert_unit(sample)


@pytest.mark.asyncio
async def test_fetch_unit_none(tmp_path, monkeypatch):
    monkeypatch.setenv("BASE_DIR", str(tmp_path))
    monkeypatch.setenv("DB_FILENAME", "test_none.db")
    import config as cfg
    importlib.reload(cfg)

    import database as db
    importlib.reload(db)

    await db.init_db()
    res = await db.fetch_unit("nonexistent")
    assert res is None