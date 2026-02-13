"""main.py — Orquestador asíncrono usando Playwright.

Plantilla mínima que sigue las reglas de `AI_CONTEXT.md`:
- API async de Playwright
- No bloqueos de I/O (uso async/await)
"""

import asyncio
import logging
from typing import Dict

from playwright.async_api import Page

from config import PLAYWRIGHT_TIMEOUT_MS
from utils import download_file
from scraper import Scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_scraper(start_urls: list[str]) -> None:
    """Run the scraper using the `Scraper` class (keeps main small).

    This function preserves the previous external API but delegates behavior
    to `scraper.Scraper`, which allows injecting dependencies for testing.
    """
    s = Scraper()
    await s.run(start_urls)


def main() -> None:
    start_urls = [
        "https://example.com/unit/1",
    ]
    asyncio.run(run_scraper(start_urls))


if __name__ == "__main__":
    main()
