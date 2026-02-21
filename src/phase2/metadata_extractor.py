"""Project Metadata Extractor.

Extracts project information:
- Title, description
- Status, delivery date, zone
- Price, developer contact.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract project metadata from page."""

    def __init__(self, page):
        """Initialize with a Playwright page object."""
        self.page = page

    async def extract_all(self) -> Dict:
        """Extract all available metadata."""
        metadata = {
            "title": await self._extract_title(),
            "description": await self._extract_description(),
            "zone": await self._extract_field("Zona"),
            "delivery_date": await self._extract_field("Entrega"),
            "delivery_date_raw": await self._extract_field("Fecha de Entrega"),
            "project_status": await self._extract_field("Estado"),
            "price_from": await self._extract_field("Precio"),
            "price_from_alt": await self._extract_field("Desde"),
            "developer": await self._extract_field("Desarrollador"),
        }
        return {k: v for k, v in metadata.items() if v}

    async def _extract_title(self) -> Optional[str]:
        """Extract project title from H1 or similar."""
        try:
            title_elem = await self.page.query_selector("h1, h1.project-title, [class*='title'] h1")
            if title_elem:
                text = await title_elem.text_content()
                return text.strip() if text else None
        except Exception as e:
            logger.debug(f"Error extracting title: {e}")
        return None

    async def _extract_description(self) -> Optional[str]:
        """Extract project description."""
        try:
            # Try multiple selectors
            selectors = [
                "[class*='description']",
                "p:first-of-type",
                "article p:first-child",
                "[class*='overview']",
            ]

            for selector in selectors:
                elem = await self.page.query_selector(selector)
                if elem:
                    text = await elem.text_content()
                    if text and len(text.strip()) > 50:  # Only if substantial
                        return text.strip()[:500]
        except Exception as e:
            logger.debug(f"Error extracting description: {e}")
        return None

    async def _extract_field(self, label_text: str) -> Optional[str]:
        """Extract a labeled field value (e.g., 'Zona: Centro')."""
        try:
            # Find label with text
            labels = await self.page.query_selector_all(
                f"label, strong, dt, span:has-text('{label_text}')"
            )

            for label in labels:
                label_text_check = await label.text_content()
                if label_text in label_text_check:
                    # Get next sibling or value
                    parent = await label.evaluate("el => el.parentElement")
                    if parent:
                        # Try to find value in parent
                        value_elem = await parent.query_selector("span, p, dd, td:nth-child(2)")
                        if value_elem:
                            value = await value_elem.text_content()
                            return value.strip() if value else None

                    # Try next sibling
                    value_elem = await label.query_selector(":next-sibling()")
                    if value_elem:
                        value = await value_elem.text_content()
                        return value.strip() if value else None

        except Exception as e:
            logger.debug(f"Error extracting field '{label_text}': {e}")

        return None

    async def extract_summary(self) -> str:
        """Get human-readable summary of extracted metadata."""
        metadata = await self.extract_all()
        lines = ["📄 Project Metadata:"]

        for key, value in metadata.items():
            if value:
                # Format key name
                display_key = key.replace("_", " ").title()
                lines.append(f"  • {display_key}: {value[:50]}")

        return "\n".join(lines)
