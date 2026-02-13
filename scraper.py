"""scraper.py — Encapsula la lógica de scraping y permite inyección de dependencias.

Separa responsabilidades: manejo del browser, scraping de una unidad y persistencia.
Permite pasar un `browser_factory`, `db_manager` y `downloader` para facilitar tests.
"""

from typing import Callable, Awaitable
from pathlib import Path
import logging

from playwright.async_api import async_playwright

from config import PLAYWRIGHT_HEADLESS, PLAYWRIGHT_TIMEOUT_MS, USER_AGENT, DB_PATH
from db_manager import DBManager
from downloader import Downloader

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(
        self,
        browser_factory: Callable[[], Awaitable] | None = None,
        db_manager: DBManager | None = None,
        downloader: Downloader | None = None,
    ) -> None:
        self.browser_factory = browser_factory or async_playwright
        self.db_manager = db_manager or DBManager(DB_PATH)
        self.downloader = downloader or Downloader()

    async def scrape_unit_page(self, page, unit_url: str) -> dict:
        """Extrae datos de una unidad; maneja errores y retorna un dict.

        Esta función es pequeña y fácil de testear aislada.
        """
        try:
            await page.goto(unit_url, timeout=PLAYWRIGHT_TIMEOUT_MS)
            title = await page.text_content("h1") or ""
            price_text = await page.text_content(".price") or ""
            return {"url": unit_url, "title": title.strip(), "price_raw": price_text.strip()}
        except Exception as exc:
            logger.exception("Error al scrapear %s: %s", unit_url, exc)
            return {"url": unit_url, "error": str(exc)}

    async def run(self, start_urls: list[str]) -> None:
        """Orquesta el navegador y procesa `start_urls`.

        Usa `browser_factory` para crear el contexto de Playwright (facilita tests).
        """
        await self.db_manager.init()

        async with self.browser_factory() as pw:
            browser = await pw.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
            context = await browser.new_context(user_agent=USER_AGENT)
            page = await context.new_page()

            for url in start_urls:
                data = await self.scrape_unit_page(page, url)
                if "error" not in data:
                    await self.db_manager.insert_unit(data)

            try:
                await context.close()
            except Exception:
                pass
            try:
                await browser.close()
            except Exception:
                pass
