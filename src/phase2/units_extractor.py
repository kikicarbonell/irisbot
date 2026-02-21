"""
Units Table Extractor

Extracts apartment/unit information from project pages:
- Typology (1 BR, 2 BR, Garage, etc)
- Square meters (internal, external)
- Prices (from, to, rent)
- Availability, 360 view, etc
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class UnitsExtractor:
    """Extract units/apartments table from project page."""

    def __init__(self, page):
        """Initialize with a Playwright page object."""
        self.page = page

    async def extract_all(self) -> Tuple[bool, List[Dict]]:
        """
        Extract all units from page.

        Returns:
            (found: bool, units: List[Dict])
            - found: whether a units table was found
            - units: list of extracted unit objects
        """
        # Try to find the table
        table = await self._find_table()
        if not table:
            logger.warning("No units table found")
            return False, []

        logger.info("✓ Units table found")

        # Extract headers to understand columns
        headers = await self._extract_headers(table)
        if not headers:
            logger.warning("Could not extract table headers")
            return False, []

        logger.info(f"Table headers: {headers}")

        # Extract rows
        rows = await self._extract_rows(table, headers)
        logger.info(f"Extracted {len(rows)} units")

        return True, rows

    async def _find_table(self):
        """Find the units table on the page."""
        # Try various selectors in priority order
        selectors = [
            "table",
            "table.units-table",
            "table[class*='unit']",
            "table[class*='apartment']",
            'div[role="table"]',
            'div[class*="table-responsive"] table',
            '[class*="units-container"] table',
        ]

        for selector in selectors:
            try:
                table = await self.page.query_selector(selector)
                if table:
                    return table
            except:
                pass

        return None

    async def _extract_headers(self, table) -> List[str]:
        """Extract column headers from table."""
        headers = []

        try:
            # Try thead first
            header_row = await table.query_selector("thead tr, tr:first-child")
            if not header_row:
                return headers

            header_cells = await header_row.query_selector_all("th, td")

            for cell in header_cells:
                text = await cell.text_content()
                if text:
                    headers.append(text.strip())

        except Exception as e:
            logger.debug(f"Error extracting headers: {e}")

        return headers

    async def _extract_rows(self, table, headers: List[str]) -> List[Dict]:
        """Extract data rows from table."""
        units = []

        try:
            # Find tbody or all data rows
            rows = await table.query_selector_all("tbody tr, tr:not(:first-child)")

            for row_idx, row in enumerate(rows[:100]):  # Limit to 100 units
                try:
                    cells = await row.query_selector_all("td, th")
                    cell_values = []

                    for cell in cells:
                        text = await cell.text_content()
                        cell_values.append(text.strip() if text else "")

                    # Build unit object from cells and headers
                    unit = self._parse_unit_row(cell_values, headers, row_idx)
                    if unit:
                        units.append(unit)

                except Exception as e:
                    logger.debug(f"Error extracting row {row_idx}: {e}")

        except Exception as e:
            logger.debug(f"Error extracting rows: {e}")

        return units

    def _parse_unit_row(
        self, cell_values: List[str], headers: List[str], row_idx: int
    ) -> Optional[Dict]:
        """
        Parse a single row into a unit object.

        Handles various column configurations and data formats.
        """
        if not cell_values:
            return None

        unit = {
            "id": f"unit_{row_idx}",
            "row_index": row_idx,
            "raw_cells": cell_values,
        }

        # Map cell values to common fields
        # This is heuristic-based and may need adjustment per project

        unit["typology"] = cell_values[0] if len(cell_values) > 0 else None

        # Try to identify remaining columns
        for i, cell in enumerate(cell_values):
            cell_lower = cell.lower()

            # Square meters
            if "m²" in cell or "m2" in cell or "sqm" in cell_lower:
                if "interno" in (headers[i].lower() if i < len(headers) else ""):
                    unit["internal_sqm"] = self._parse_number(cell)
                elif "externo" in (headers[i].lower() if i < len(headers) else ""):
                    unit["external_sqm"] = self._parse_number(cell)
                elif "total" in (headers[i].lower() if i < len(headers) else ""):
                    unit["total_sqm"] = self._parse_number(cell)

            # Prices
            elif "$" in cell or "usd" in cell_lower or "desde" in cell_lower:
                if "desde" in (headers[i].lower() if i < len(headers) else ""):
                    unit["price_from"] = self._parse_price(cell)
                elif "hasta" in (headers[i].lower() if i < len(headers) else ""):
                    unit["price_to"] = self._parse_price(cell)

            # Boolean flags
            elif cell_lower in ["sí", "si", "yes", "true", "✓", "x"]:
                if "alquiler" in (headers[i].lower() if i < len(headers) else ""):
                    unit["rent_available"] = True
                elif "360" in (headers[i] if i < len(headers) else ""):
                    unit["has_360_view"] = True

        return unit

    def _parse_number(self, text: str) -> Optional[float]:
        """Extract numeric value from text."""
        try:
            # Remove common non-numeric characters
            cleaned = text.replace("m²", "").replace("m2", "").replace(",", ".").strip()
            return float(cleaned)
        except ValueError:
            return None

    def _parse_price(self, text: str) -> Optional[int]:
        """Extract price as integer from text."""
        try:
            # Remove currency symbols and convert
            cleaned = (
                text.replace("$", "").replace("USD", "").replace(",", "").replace(".", "").strip()
            )
            return int(cleaned)
        except ValueError:
            return None

    async def extract_summary(self) -> str:
        """Get human-readable summary of extracted units."""
        found, units = await self.extract_all()

        if not found:
            return "📊 Units Table: Not found"

        summary = [f"📊 Units Table: {len(units)} units found"]

        # Group by typology
        typologies = {}
        for unit in units:
            typo = unit.get("typology", "Unknown")
            typologies[typo] = typologies.get(typo, 0) + 1

        for typo, count in sorted(typologies.items()):
            summary.append(f"  • {typo}: {count}")

        return "\n".join(summary)
