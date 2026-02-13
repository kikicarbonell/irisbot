"""main.py — Orquestador asíncrono usando Playwright.

Plantilla mínima que sigue las reglas de `AI_CONTEXT.md`:
- API async de Playwright
- No bloqueos de I/O (uso async/await)
"""

import asyncio
import logging
from typing import Dict

from playwright.async_api import async_playwright, Page

from config import PLAYWRIGHT_HEADLESS, PLAYWRIGHT_TIMEOUT_MS, USER_AGENT
from database import init_db, insert_unit
from utils import download_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scrape_unit_page(page: Page, unit_url: str) -> Dict:
    """Placeholder: extrae datos de una unidad dada su URL.

    Debe manejar fallos de selectores y devolver dict con campos esperados.
    """
    try:
        await page.goto(unit_url, timeout=PLAYWRIGHT_TIMEOUT_MS)
        # Ejemplo: obtener título y precio (reemplazar selectores reales)
        title = await page.text_content("h1") or ""
        price_text = await page.text_content(".price") or ""
        # Normalizar/parsear según reglas del proyecto
        return {"url": unit_url, "title": title.strip(), "price_raw": price_text.strip()}
    except Exception as exc:  # noqa: BLE001 - registrar y continuar
        logger.exception("Error al scrapear %s: %s", unit_url, exc)
        return {"url": unit_url, "error": str(exc)}


async def run_scraper(start_urls: list[str]) -> None:
    await init_db()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()

        for url in start_urls:
            data = await scrape_unit_page(page, url)
            # Guardar en DB si trae datos válidos
            if "error" not in data:
                await insert_unit(data)
            # Si hay assets para descargar, usar download_file desde `utils.py`
            # await download_file(session, asset_url, dest_path)

        await context.close()
        await browser.close()


def main() -> None:
    start_urls = [
        "https://example.com/unit/1",
    ]
    asyncio.run(run_scraper(start_urls))


if __name__ == "__main__":
    main()
