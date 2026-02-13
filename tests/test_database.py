import importlib
import os
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_init_insert_fetch(tmp_path, monkeypatch):
    # Point DB to a temp file via BASE_DIR so config.DB_PATH resolves there
    monkeypatch.setenv("BASE_DIR", str(tmp_path))
    monkeypatch.setenv("DB_FILENAME", "test_irisbot.db")

    import config as cfg
    importlib.reload(cfg)

    import database as db
    importlib.reload(db)

    # Init DB
    await db.init_db()
    assert cfg.DB_PATH.exists()

    sample = {"url": "http://example.com/u/1", "title": "Unit 1", "price_raw": "$100"}
    await db.insert_unit(sample)

    fetched = await db.fetch_unit(sample["url"])
    assert fetched is not None
    assert fetched["url"] == sample["url"]
    assert fetched["title"] == sample["title"]
