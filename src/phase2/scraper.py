"""
Phase 2 Project Details Scraper

Main scraper for extracting complete project details:
- Metadata (description, status, etc)
- Units table
- Developer information
- Downloadable assets
"""

import asyncio
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import authenticate
from config import IRIS_BASE_URL, LOG_LEVEL, PLAYWRIGHT_HEADLESS
from phase2.assets_extractor import AssetsExtractor
from phase2.developer_extractor import DeveloperExtractor
from phase2.metadata_extractor import MetadataExtractor
from phase2.units_extractor import UnitsExtractor

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

DB_PATH = Path("catalog_projects.db")


class Phase2Scraper:
    """Scrape complete project details."""

    def __init__(self, page: Page, project_id: int, base_url: str = IRIS_BASE_URL):
        """Initialize scraper for a specific project."""
        self.page = page
        self.project_id = project_id
        self.base_url = base_url
        self.url = f"{base_url}/proyecto/{project_id}"

    async def navigate(self) -> bool:
        """Navigate to project page and wait for content."""
        try:
            logger.info(f"🔗 Navigating to project {self.project_id}")
            await self.page.goto(self.url, wait_until="networkidle", timeout=30000)
            logger.info(f"✓ Page loaded: {self.page.url}")
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"⏱️  Timeout navigating to project {self.project_id}")
            return False
        except Exception as e:
            logger.error(f"✗ Error navigating to project {self.project_id}: {e}")
            return False

    async def extract_all(self) -> Dict:
        """Extract all available data from project page."""
        result = {
            "project_id": self.project_id,
            "url": self.url,
            "success": True,
            "metadata": {},
            "units": {"found": False, "count": 0, "data": []},
            "developer": {},
            "assets": [],
            "errors": [],
        }

        try:
            # Extract metadata
            logger.info("📄 Extracting metadata...")
            meta_extractor = MetadataExtractor(self.page)
            result["metadata"] = await meta_extractor.extract_all()
            logger.debug(await meta_extractor.extract_summary())

            # Extract units
            logger.info("📊 Extracting units...")
            units_extractor = UnitsExtractor(self.page)
            found, units = await units_extractor.extract_all()
            result["units"]["found"] = found
            result["units"]["count"] = len(units)
            result["units"]["data"] = units
            logger.debug(await units_extractor.extract_summary())

            # Extract developer info
            logger.info("👨‍💼 Extracting developer info...")
            dev_extractor = DeveloperExtractor(self.page)
            result["developer"] = await dev_extractor.extract_all()
            logger.debug(await dev_extractor.extract_summary())

            # Extract assets
            logger.info("📥 Extracting assets...")
            assets_extractor = AssetsExtractor(self.page, base_url=self.base_url)
            result["assets"] = await assets_extractor.extract_all()
            logger.debug(await assets_extractor.extract_summary())

        except Exception as e:
            logger.error(f"✗ Error during extraction: {e}")
            result["success"] = False
            result["errors"].append(str(e))

        return result

    async def save_extraction(
        self, data: Dict, output_dir: Path = Path("phase2_extractions")
    ) -> bool:
        """Save extraction results to JSON file."""
        try:
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"project_{self.project_id}_extraction.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✓ Saved extraction to {output_file}")
            return True
        except Exception as e:
            logger.error(f"✗ Error saving extraction: {e}")
            return False

    async def save_to_db(self, data: Dict) -> bool:
        """Save extracted data to database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            # Update projects table with metadata
            metadata = data.get("metadata", {})
            c.execute(
                """
                UPDATE projects SET
                    description = ?,
                    amenities = ?,
                    delivery_date = ?,
                    developer_email = ?,
                    developer_phone = ?,
                    phase2_scraped_at = CURRENT_TIMESTAMP,
                    phase2_updated_at = CURRENT_TIMESTAMP
                WHERE project_id = ?
            """,
                (
                    metadata.get("description"),
                    json.dumps(metadata.get("amenities", [])),
                    metadata.get("delivery_date"),
                    metadata.get("developer_email"),
                    metadata.get("developer_phone"),
                    self.project_id,
                ),
            )

            # Insert units
            units = data.get("units", {}).get("data", [])
            for unit in units:
                unit_id = f"{self.project_id}_{unit.get('row_index', 0)}"
                c.execute(
                    """
                    INSERT OR REPLACE INTO units (
                        id, project_id, typology, internal_sqm, external_sqm,
                        total_sqm, price_from, price_to, rent_available,
                        has_360_view, status, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        unit_id,
                        self.project_id,
                        unit.get("typology"),
                        unit.get("internal_sqm"),
                        unit.get("external_sqm"),
                        unit.get("total_sqm"),
                        unit.get("price_from"),
                        unit.get("price_to"),
                        unit.get("rent_available", False),
                        unit.get("has_360_view", False),
                        unit.get("status"),
                        json.dumps(unit, default=str),
                    ),
                )

            # Insert developer info
            developer = data.get("developer", {})
            if developer:
                c.execute(
                    """
                    INSERT OR REPLACE INTO developer_info (
                        project_id, company_name, company_email, company_phone,
                        company_website, logo_url, description, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        self.project_id,
                        developer.get("company_name"),
                        developer.get("contact_email"),
                        developer.get("contact_phone"),
                        developer.get("website"),
                        developer.get("logo_url"),
                        None,  # description not extracted yet
                        json.dumps(developer, default=str),
                    ),
                )

            # Insert assets
            assets = data.get("assets", [])
            for i, asset in enumerate(assets):
                asset_id = f"{self.project_id}_asset_{i}"
                c.execute(
                    """
                    INSERT OR REPLACE INTO developer_assets (
                        id, project_id, asset_type, asset_name, file_url, file_type
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        asset_id,
                        self.project_id,
                        asset.get("type"),
                        asset.get("text"),
                        asset.get("url"),
                        asset.get("file_type"),
                    ),
                )

            conn.commit()
            conn.close()

            logger.info(f"✓ Saved data to database for project {self.project_id}")
            return True

        except Exception as e:
            logger.error(f"✗ Error saving to database: {e}")
            return False


async def scrape_single_project(project_id: int) -> Dict:
    """Scrape a single project and save results."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
        page = await browser.new_page()

        try:
            # Authenticate
            logger.info("🔐 Authenticating...")
            success = await authenticate(page)
            if not success:
                logger.error("Authentication failed")
                return {
                    "project_id": project_id,
                    "success": False,
                    "error": "Authentication failed",
                }

            # Create scraper
            scraper = Phase2Scraper(page, project_id)

            # Navigate
            if not await scraper.navigate():
                return {"project_id": project_id, "success": False, "error": "Navigation failed"}

            # Extract
            data = await scraper.extract_all()

            # Save
            await scraper.save_extraction(data)
            await scraper.save_to_db(data)

            return data

        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return {"project_id": project_id, "success": False, "error": str(e)}
        finally:
            await browser.close()


async def scrape_multiple_projects(project_ids: list, limit_per_run: int = 5) -> Dict:
    """Scrape multiple projects."""
    logger.info(f"🚀 Starting Phase 2 scraping for {len(project_ids)} projects\n")

    results = {"total": len(project_ids), "successful": 0, "failed": 0, "projects": []}

    for i, project_id in enumerate(project_ids[:limit_per_run], 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"PROJECT {i}/{min(len(project_ids), limit_per_run)}: ID {project_id}")
        logger.info(f"{'='*80}\n")

        result = await scrape_single_project(project_id)
        results["projects"].append(result)

        if result.get("success"):
            results["successful"] += 1
        else:
            results["failed"] += 1

        # Rate limiting
        if i < len(project_ids):
            await asyncio.sleep(2)

    return results


async def main():
    """Main entry point."""
    # Get projects from database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT project_id FROM projects LIMIT 5")
    rows = c.fetchall()
    conn.close()

    project_ids = [row[0] for row in rows]

    if not project_ids:
        logger.error("No projects found in database")
        return

    logger.info(f"Using projects: {project_ids}\n")

    # Scrape
    results = await scrape_multiple_projects(project_ids, limit_per_run=3)

    # Print summary
    logger.info(f"\n{'='*80}")
    logger.info("📊 PHASE 2 SCRAPING SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Total projects: {results['total']}")
    logger.info(f"Successful: {results['successful']} ✓")
    logger.info(f"Failed: {results['failed']} ✗")
    logger.info(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
