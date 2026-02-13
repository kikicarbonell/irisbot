"""Additional edge-case tests to push coverage >90%"""

import asyncio
import pytest


class FakePage:
    def __init__(self, title="Title", price="$100"):
        self.title = title
        self.price = price

    async def goto(self, url, timeout=None):
        return None

    async def text_content(self, selector):
        if selector == "h1":
            return self.title
        if selector == ".price":
            return self.price
        return ""


class FakeContext:
    def __init__(self, page):
        self.page = page

    async def new_page(self):
        return self.page

    async def close(self):
        pass


class FakeBrowser:
    def __init__(self, page):
        self.context = FakeContext(page)

    async def new_context(self, user_agent=None):
        return self.context

    async def close(self):
        pass


class FakeChromium:
    def __init__(self, page):
        self.page = page

    async def launch(self, headless=True):
        return FakeBrowser(self.page)


class FakePlaywright:
    def __init__(self, page):
        self.chromium = FakeChromium(page)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_scraper_multiple_urls():
    """Test scraper with multiple URLs"""
    from scraper import Scraper

    class FakeDBManager:
        def __init__(self):
            self.inserts = []

        async def init(self):
            pass

        async def insert_unit(self, data):
            self.inserts.append(data)

    page = FakePage(title="TestUnit", price="$100")
    browser_factory = lambda: FakePlaywright(page)
    db_mgr = FakeDBManager()
    s = Scraper(browser_factory=browser_factory, db_manager=db_mgr)

    await s.run(["http://fake/u1", "http://fake/u2", "http://fake/u3"])

    assert len(db_mgr.inserts) == 3
    assert all(d["title"] == "TestUnit" for d in db_mgr.inserts)


@pytest.mark.asyncio
async def test_db_manager_metadata_json_error(tmp_path):
    """Test DBManager.fetch_unit with malformed JSON in metadata"""
    from db_manager import DBManager
    import aiosqlite

    db_path = tmp_path / "bad_json.db"
    mgr = DBManager(db_path)
    await mgr.init()

    await mgr.insert_unit({"url": "http://example.com/u1", "title": "T1", "price_raw": "$1"})

    async with aiosqlite.connect(db_path.as_posix()) as db:
        await db.execute("UPDATE units SET metadata = ? WHERE url = ?", ("invalid json {{{", "http://example.com/u1"))
        await db.commit()

    res = await mgr.fetch_unit("http://example.com/u1")
    assert res is not None
    assert res["url"] == "http://example.com/u1"
    assert "raw_metadata" in res


@pytest.mark.asyncio
async def test_downloader_http_403_error(tmp_path):
    """Test downloader with 403 Forbidden"""
    from downloader import Downloader
    from aioresponses import aioresponses

    url = "https://example.com/forbidden.bin"
    dest = tmp_path / "forbidden.bin"

    with aioresponses() as m:
        m.get(url, status=403)
        m.get(url, status=403)
        m.get(url, status=403)
        dl = Downloader()
        result = await dl.download(url, dest)

        assert result is None
        assert not dest.exists()


@pytest.mark.asyncio
async def test_db_manager_multiple_inserts(tmp_path):
    """Test DBManager with repeated inserts of same unit"""
    from db_manager import DBManager

    db_path = tmp_path / "multi.db"
    mgr = DBManager(db_path)
    await mgr.init()

    await mgr.insert_unit({"url": "http://example.com/u1", "title": "T1", "price_raw": "$100"})
    await mgr.insert_unit({"url": "http://example.com/u1", "title": "T1_Updated", "price_raw": "$200"})

    res = await mgr.fetch_unit("http://example.com/u1")
    assert res is not None
    assert res["title"] == "T1_Updated"
    assert res["price_raw"] == "$200"
