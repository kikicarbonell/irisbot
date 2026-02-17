"""Unit tests for db_manager.py"""

import pytest


@pytest.mark.asyncio
async def test_db_manager_init_and_insert(tmp_path):
    from db_manager import DBManager

    db_path = tmp_path / "test.db"
    mgr = DBManager(db_path)
    await mgr.init()

    assert db_path.exists()

    sample = {"url": "http://example.com/u1", "title": "Unit 1", "price_raw": "$100"}
    await mgr.insert_unit(sample)

    fetched = await mgr.fetch_unit(sample["url"])
    assert fetched is not None
    assert fetched["url"] == sample["url"]
    assert fetched["title"] == sample["title"]


@pytest.mark.asyncio
async def test_db_manager_fetch_none(tmp_path):
    from db_manager import DBManager

    db_path = tmp_path / "test2.db"
    mgr = DBManager(db_path)
    await mgr.init()

    res = await mgr.fetch_unit("nonexistent")
    assert res is None


@pytest.mark.asyncio
async def test_db_manager_insert_with_metadata(tmp_path):
    from db_manager import DBManager

    db_path = tmp_path / "test3.db"
    mgr = DBManager(db_path)
    await mgr.init()

    sample = {
        "url": "http://example.com/u2",
        "title": "Unit 2",
        "price_raw": "$200",
        "custom_field": "custom_value",
    }
    await mgr.insert_unit(sample)

    fetched = await mgr.fetch_unit(sample["url"])
    assert fetched is not None
    assert fetched.get("custom_field") == "custom_value"
