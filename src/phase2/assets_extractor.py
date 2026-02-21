"""Assets Extractor.

Finds and extracts downloadable files:
- PDFs (brochures, floor plans, memoria descriptiva)
- Images (project photos, logo)
- Other documents.
"""

import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class AssetsExtractor:
    """Extract downloadable assets from project page."""

    ASSET_TYPES = {
        "brochure": ["brochure", "folleto", "prospecto"],
        "floor_plans": ["planos", "floor", "plan", "plantas"],
        "memoria": ["memoria", "descriptiva", "memoria descriptiva"],
        "logo": ["logo", "logotipo"],
        "image": [".jpg", ".png", ".jpeg"],
    }

    def __init__(self, page, base_url: str = "https://iris.infocasas.com.uy"):
        """Initialize with a Playwright page object."""
        self.page = page
        self.base_url = base_url

    async def extract_all(self) -> List[Dict]:
        """Extract all downloadable assets from page."""
        assets = []

        try:
            # Find all links
            links = await self.page.query_selector_all("a[href]")
            logger.info(f"Found {len(links)} links on page")

            for link in links:
                href = await link.get_attribute("href")
                text = await link.text_content()

                if not href:
                    continue

                # Make full URL
                full_url = urljoin(self.base_url, href)

                # Check if it's a file
                asset = self._parse_asset(href, text, full_url)
                if asset:
                    assets.append(asset)

                # Limit to 50 assets
                if len(assets) >= 50:
                    break

        except Exception as e:
            logger.debug(f"Error extracting assets: {e}")

        # Remove duplicates
        unique_assets = {a["url"]: a for a in assets}
        assets = list(unique_assets.values())

        logger.info(f"Extracted {len(assets)} unique assets")
        return sorted(assets, key=lambda x: x["type"])

    def _parse_asset(self, href: str, link_text: str, full_url: str) -> Optional[Dict]:
        """Determine if a link is an asset file and classify it.

        Returns:
            Dict with asset info or None if not an asset.
        """
        href_lower = href.lower()
        text_lower = link_text.lower() if link_text else ""

        # Get file extension
        if "." not in href_lower:
            return None

        file_ext = href_lower.split(".")[-1].split("?")[0]

        # Only keep file extensions we care about
        valid_extensions = ["pdf", "jpg", "jpeg", "png", "zip", "doc", "docx"]
        if file_ext not in valid_extensions:
            return None

        # Classify by type
        asset_type = self._classify_asset(href_lower, text_lower)

        asset = {
            "url": full_url,
            "text": link_text[:100] if link_text else "Download",
            "type": asset_type,
            "file_type": file_ext.upper(),
        }

        return asset

    def _classify_asset(self, href_lower: str, text_lower: str) -> str:
        """Classify asset by type."""
        combined = f"{href_lower} {text_lower}"

        for asset_type, keywords in self.ASSET_TYPES.items():
            if any(keyword in combined for keyword in keywords):
                return asset_type

        return "file"

    async def extract_summary(self) -> str:
        """Get human-readable summary of extracted assets."""
        assets = await self.extract_all()

        if not assets:
            return "📥 Assets: None found"

        summary = [f"📥 Assets: {len(assets)} files"]

        # Group by type
        by_type = {}
        for asset in assets:
            asset_type = asset["type"]
            by_type[asset_type] = by_type.get(asset_type, 0) + 1

        for asset_type, count in sorted(by_type.items()):
            summary.append(f"  • {asset_type}: {count}")

        return "\n".join(summary)
