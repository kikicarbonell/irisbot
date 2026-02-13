import importlib
import asyncio

import pytest


class FakePage:
    async def goto(self, url, timeout=None):
        return None

    async def text_content(self, selector):
        if selector == "h1":
            return "Faked Title"
        if selector == ".price":
            return "$999"
        return ""


class FakeContext:
    def __init__(self):
        self.page = FakePage()

    async def new_page(self):
        return self.page

    async def close(self):
        return None


class FakeBrowser:
    def __init__(self):
        self.context = FakeContext()

    async def new_context(self, user_agent=None):
        return self.context

    async def close(self):
        return None


class FakeChromium:
    def __init__(self):
        pass

    async def launch(self, headless=True):
        return FakeBrowser()


class FakePlaywright:
    def __init__(self):
        self.chromium = FakeChromium()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_run_scraper_calls_insert(monkeypatch):
    # Create Scraper with injected browser factory and fake insert/init functions
    from scraper import Scraper

    from db_manager import DBManager

    called = []

    class FakeDBManager:
        async def init(self):
            return None

        async def insert_unit(self, data):
            called.append(data)

    browser_factory = lambda: FakePlaywright()
    db_mgr = FakeDBManager()

    s = Scraper(browser_factory=browser_factory, db_manager=db_mgr)
    await s.run(["http://fake/unit/1"])
    assert len(called) == 1
    assert called[0]["title"] == "Faked Title"
