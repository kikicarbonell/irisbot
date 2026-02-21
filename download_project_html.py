#!/usr/bin/env python3
"""
Download HTML content from project detail pages for offline analysis.
"""

import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent / "src"))

from auth import authenticate
from config import IRIS_BASE_URL, LOG_LEVEL, PLAYWRIGHT_HEADLESS
import logging

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("phase2_analysis")


async def download_project_html(project_id: int) -> bool:
    """Download and save HTML for a project."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
        page = await browser.new_page()

        try:
            # Authenticate
            logger.info(f"Authenticating...")
            success = await authenticate(page)
            if not success:
                logger.error("Authentication failed")
                return False

            # Navigate to project
            url = f"{IRIS_BASE_URL}/proyecto/{project_id}"
            logger.info(f"Downloading: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Get page content
            html_content = await page.content()

            # Save to file
            OUTPUT_DIR.mkdir(exist_ok=True)
            output_file = OUTPUT_DIR / f"proyecto_{project_id}.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"✓ Saved: {output_file} ({len(html_content)} bytes)")

            # Also save page info
            info_file = OUTPUT_DIR / f"proyecto_{project_id}_info.json"
            info = {
                "project_id": project_id,
                "url": url,
                "title": await page.title(),
                "html_size": len(html_content),
            }
            with open(info_file, "w") as f:
                json.dump(info, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Error downloading project {project_id}: {e}")
            return False
        finally:
            await browser.close()


async def main():
    """Download HTMLs for multiple projects."""
    project_ids = [1, 237, 1236]  # From earlier query

    logger.info(f"Downloading HTML for {len(project_ids)} projects\n")

    for project_id in project_ids:
        success = await download_project_html(project_id)
        if success:
            await asyncio.sleep(2)  # Rate limit

    logger.info(f"\n✓ Downloaded to: {OUTPUT_DIR.resolve()}")
    logger.info(f"Next: Run 'python3 analyze_project_html.py' to analyze\n")


if __name__ == "__main__":
    asyncio.run(main())
