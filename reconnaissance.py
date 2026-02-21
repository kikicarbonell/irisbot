#!/usr/bin/env python3
"""
Reconnaissance script for Phase 2: Project Detail Scraping

This script analyzes the structure of project detail pages to identify:
- CSS selectors for project metadata
- Units table structure
- Developer information modals
- Asset download locations
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import Page, async_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from auth import authenticate
from config import IRIS_BASE_URL, LOG_LEVEL, PLAYWRIGHT_HEADLESS

logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Output directory for analysis
ANALYSIS_DIR = Path("phase2_research")


class ProjectDetailAnalyzer:
    """Analyze structure of a project detail page."""

    def __init__(self, page: Page):
        self.page = page
        self.project_id = None

    async def navigate_to_project(self, project_id: int) -> bool:
        """Navigate to a specific project detail page."""
        url = f"{IRIS_BASE_URL}/proyecto/{project_id}"
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            self.project_id = project_id
            logger.info(f"✓ Navigated to project {project_id}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to navigate to project {project_id}: {e}")
            return False

    async def analyze_page_structure(self) -> Dict:
        """Analyze the overall structure of the page."""
        analysis = {
            "url": self.page.url,
            "project_id": self.project_id,
            "title": await self.page.title() if self.page else None,
            "sections": [],
        }

        # Find main content areas
        sections = await self.page.query_selector_all("section, div[class*='section'], main")
        logger.info(f"Found {len(sections)} main sections")

        for i, section in enumerate(sections):
            section_info = {
                "index": i,
                "tag": await section.evaluate("el => el.tagName"),
                "class": await section.evaluate("el => el.className"),
                "text_preview": (await section.text_content())[:100],
            }
            analysis["sections"].append(section_info)

        return analysis

    async def analyze_project_metadata(self) -> Dict:
        """Extract project metadata (name, description, etc)."""
        metadata = {}

        # Project title/name
        try:
            title = await self.page.query_selector("h1, h2, [class*='title'], [class*='heading']")
            if title:
                metadata["title"] = await title.text_content()
                logger.info(f"✓ Project title: {metadata['title'][:50]}")
        except Exception as e:
            logger.warning(f"Could not extract title: {e}")

        # Description/Overview
        try:
            desc_selectors = [
                "[class*='description']",
                "[class*='overview']",
                "div:has(> p:nth-child(-n+3))",
                "article p",
            ]
            for selector in desc_selectors:
                desc = await self.page.query_selector(selector)
                if desc:
                    text = await desc.text_content()
                    if len(text.strip()) > 50:
                        metadata["description"] = text[:200]
                        logger.info(f"✓ Description found ({len(text)} chars)")
                        break
        except Exception as e:
            logger.warning(f"Could not extract description: {e}")

        # Key metadata fields
        metadata_fields = {}
        try:
            # Look for label-value pairs
            labels = await self.page.query_selector_all(
                "label, span:has-text(/zona|ubicación|entrega|precio|desarrollador/i)",
                strict=False
            )
            logger.info(f"Found {len(labels)} potential metadata fields")

            for label in labels[:10]:  # Limit to first 10
                text = await label.text_content()
                if text:
                    metadata_fields[text.strip()] = {
                        "element": await label.evaluate("el => el.tagName"),
                        "parent_class": await label.evaluate("el => el.parentElement?.className"),
                    }
        except Exception as e:
            logger.warning(f"Could not analyze metadata fields: {e}")

        metadata["fields"] = metadata_fields
        return metadata

    async def analyze_units_table(self) -> Dict:
        """Analyze the units/apartments table structure."""
        units = {
            "found": False,
            "selector": None,
            "structure": None,
            "sample_rows": [],
            "columns": [],
        }

        # Try different table selectors
        table_selectors = [
            "table",
            "table.units-table",
            "table[class*='unit']",
            '[role="table"]',
            'div[class*="table-responsive"] table',
        ]

        table = None
        for selector in table_selectors:
            try:
                table = await self.page.query_selector(selector)
                if table:
                    units["selector"] = selector
                    logger.info(f"✓ Found units table with selector: {selector}")
                    break
            except:
                pass

        if not table:
            logger.warning("✗ Could not find units table")
            return units

        units["found"] = True

        # Analyze table structure
        try:
            # Get headers
            headers = await table.query_selector_all("thead th, thead td, tr:first-child th")
            units["columns"] = [
                {"text": await h.text_content(), "tag": await h.evaluate("el => el.tagName")}
                for h in headers
            ]
            logger.info(f"✓ Table columns: {[c['text'].strip() for c in units['columns']]}")
        except Exception as e:
            logger.warning(f"Could not extract table headers: {e}")

        # Get sample rows
        try:
            rows = await table.query_selector_all("tbody tr, tr:not(:first-child)")
            logger.info(f"Found {len(rows)} rows in units table")

            for i, row in enumerate(rows[:3]):  # Get first 3 rows
                cells = await row.query_selector_all("td, th")
                row_data = [
                    {
                        "text": await cell.text_content(),
                        "html": await cell.inner_html(),
                    }
                    for cell in cells
                ]
                units["sample_rows"].append({"row_index": i, "cells": row_data})
        except Exception as e:
            logger.warning(f"Could not extract sample rows: {e}")

        # Get table structure HTML
        try:
            units["structure"] = await table.evaluate(
                """
                el => ({
                    rowCount: el.querySelectorAll('tbody tr, tr:not(:first-child)').length,
                    colCount: el.querySelectorAll('thead th, tr:first-child th').length,
                    classes: el.className,
                    outerHTML: el.outerHTML.substring(0, 500)
                })
                """
            )
        except Exception as e:
            logger.warning(f"Could not get table structure: {e}")

        return units

    async def analyze_developer_info(self) -> Dict:
        """Analyze developer information modal/section."""
        dev_info = {
            "found": False,
            "modal_selector": None,
            "trigger_button": None,
            "content": None,
        }

        # Find trigger button
        button_texts = ["Más información", "Información del desarrollador", "Developer info", "Ver desarrollador"]
        for text in button_texts:
            try:
                button = await self.page.query_selector(f"button:has-text('{text}')")
                if button:
                    dev_info["trigger_button"] = text
                    dev_info["found"] = True
                    logger.info(f"✓ Found developer info button: '{text}'")

                    # Click button to reveal modal
                    await button.click()
                    await asyncio.sleep(1)

                    # Look for modal
                    modal_selectors = [
                        "[role='dialog']",
                        ".modal, .modal-content",
                        "div[class*='modal']",
                        "div:has(> button:has-text('Cerrar'))",
                    ]

                    for modal_sel in modal_selectors:
                        modal = await self.page.query_selector(modal_sel)
                        if modal:
                            dev_info["modal_selector"] = modal_sel
                            content = await modal.text_content()
                            dev_info["content"] = content[:500]
                            logger.info(f"✓ Modal found with selector: {modal_sel}")
                            break

                    break
            except:
                pass

        return dev_info

    async def analyze_assets(self) -> Dict:
        """Analyze downloadable assets (PDFs, images, etc)."""
        assets = {
            "found": False,
            "download_links": [],
            "file_types": set(),
        }

        try:
            # Find all download links
            links = await self.page.query_selector_all("a[href*='.pdf'], a[href*='.jpg'], a[href*='.png']")
            logger.info(f"Found {len(links)} asset links")

            for link in links[:10]:  # Get first 10
                href = await link.get_attribute("href")
                text = await link.text_content()
                if href:
                    file_type = href.split(".")[-1].upper() if "." in href else "UNKNOWN"
                    assets["download_links"].append({
                        "text": text.strip()[:50],
                        "href": href[:100],
                        "file_type": file_type,
                    })
                    assets["file_types"].add(file_type)

            assets["found"] = len(assets["download_links"]) > 0
            if assets["found"]:
                logger.info(f"✓ Asset types found: {', '.join(assets['file_types'])}")
        except Exception as e:
            logger.warning(f"Could not analyze assets: {e}")

        return assets

    async def full_analysis(self) -> Dict:
        """Run complete analysis of a project page."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Analyzing Project {self.project_id}")
        logger.info(f"{'='*80}\n")

        return {
            "project_id": self.project_id,
            "url": self.page.url,
            "timestamp": str(Path("phase2_research").resolve()),
            "page_structure": await self.analyze_page_structure(),
            "metadata": await self.analyze_project_metadata(),
            "units_table": await self.analyze_units_table(),
            "developer_info": await self.analyze_developer_info(),
            "assets": await self.analyze_assets(),
        }


async def run_reconnaissance(project_ids: List[int]):
    """Run analysis on multiple projects."""
    ANALYSIS_DIR.mkdir(exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
        page = await browser.new_page()

        try:
            # Authenticate
            logger.info("Authenticating...")
            success = await authenticate(page)
            if not success:
                logger.error("Authentication failed")
                return

            # Analyze each project
            analyses = []
            for project_id in project_ids:
                analyzer = ProjectDetailAnalyzer(page)
                if await analyzer.navigate_to_project(project_id):
                    analysis = await analyzer.full_analysis()
                    analyses.append(analysis)

                    # Save individual analysis
                    output_file = ANALYSIS_DIR / f"project_{project_id}_analysis.json"
                    with open(output_file, "w") as f:
                        json.dump(analysis, f, indent=2, default=str)
                    logger.info(f"✓ Analysis saved to {output_file}\n")

                await asyncio.sleep(2)  # Rate limit

            # Save summary
            summary = {
                "projects_analyzed": len(analyses),
                "analysis_count": {
                    "with_units_table": sum(1 for a in analyses if a.get("units_table", {}).get("found")),
                    "with_developer_info": sum(1 for a in analyses if a.get("developer_info", {}).get("found")),
                    "with_assets": sum(1 for a in analyses if a.get("assets", {}).get("found")),
                },
                "analyses": [{"project_id": a["project_id"], "url": a["url"]} for a in analyses],
            }

            summary_file = ANALYSIS_DIR / "reconnaissance_summary.json"
            with open(summary_file, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"\n{'='*80}")
            logger.info(f"✓ Reconnaissance complete!")
            logger.info(f"Summary saved to: {summary_file}")
            logger.info(f"Individual analyses saved to: {ANALYSIS_DIR}/")
            logger.info(f"{'='*80}")

        finally:
            await browser.close()


async def main():
    """Main entry point."""
    # Sample project IDs to analyze (from Phase 1)
    # These will be fetched from the database in a real scenario
    project_ids = [235, 236, 237, 238, 239]  # Sample IDs for reconnaissance

    logger.info(f"Starting reconnaissance on {len(project_ids)} projects...")
    logger.info(f"Output directory: {ANALYSIS_DIR.resolve()}\n")

    await run_reconnaissance(project_ids)


if __name__ == "__main__":
    asyncio.run(main())
