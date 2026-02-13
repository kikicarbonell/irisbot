import asyncio

import pytest


class FakePage:
    def __init__(self, raise_on_goto=False):
        self.raise_on_goto = raise_on_goto

    async def goto(self, url, timeout=None):
        if self.raise_on_goto:
            raise RuntimeError("navigation failed")
        return None

    async def text_content(self, selector):
        if selector == "h1":
            return "Title"
        if selector == ".price":
            return "$123"
        return ""


@pytest.mark.asyncio
async def test_scrape_unit_page_error():
    from scraper import Scraper

    s = Scraper()
    page = FakePage(raise_on_goto=True)
    res = await s.scrape_unit_page(page, "http://example.com/x")
    assert "error" in res


@pytest.mark.asyncio
async def test_scrape_unit_page_success():
    from scraper import Scraper

    s = Scraper()
    page = FakePage(raise_on_goto=False)
    res = await s.scrape_unit_page(page, "http://example.com/x")
    assert res.get("title") == "Title"
    assert res.get("price_raw") == "$123"
