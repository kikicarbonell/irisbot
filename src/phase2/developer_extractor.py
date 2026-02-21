"""
Developer Information Extractor

Extracts developer/company information:
- Company name, email, phone
- Website, logo
- Company description
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DeveloperExtractor:
    """Extract developer information from project page."""

    def __init__(self, page):
        """Initialize with a Playwright page object."""
        self.page = page

    async def extract_all(self) -> Dict:
        """Extract all available developer information."""
        # First check if modal can be opened
        modal_found = await self._open_developer_modal()

        dev_info = {
            "modal_found": modal_found,
            "company_name": None,
            "contact_email": None,
            "contact_phone": None,
            "website": None,
            "logo_url": None,
            "description": None,
        }

        if modal_found:
            # Extract from modal
            dev_info["company_name"] = await self._extract_field_from_modal("Nombre")
            dev_info["contact_email"] = await self._extract_field_from_modal("Email")
            dev_info["contact_phone"] = await self._extract_field_from_modal("Teléfono")
            dev_info["website"] = await self._extract_field_from_modal("Sitio Web")
            dev_info["logo_url"] = await self._extract_logo_url()

            # Close modal
            await self._close_developer_modal()
        else:
            # Try to extract from page directly
            logger.debug("Modal not found, trying direct extraction")
            dev_info["company_name"] = await self._extract_developer_name()
            dev_info["contact_email"] = await self._extract_email()
            dev_info["contact_phone"] = await self._extract_phone()

        return {k: v for k, v in dev_info.items() if v}

    async def _open_developer_modal(self) -> bool:
        """Find and click developer info button to open modal."""
        try:
            # Try various button selectors
            button_texts = [
                "Más Información",
                "Información del Desarrollador",
                "Ver Desarrollador",
                "Developer Info",
                "Developer",
            ]

            button = None
            for text in button_texts:
                button = await self.page.query_selector(f"button:has-text('{text}')")
                if button:
                    logger.debug(f"Found developer button: '{text}'")
                    break

            if not button:
                # Try generic button click by location
                buttons = await self.page.query_selector_all("button")
                for btn in buttons:
                    btn_text = await btn.text_content()
                    if btn_text and any(
                        keyword in btn_text.lower() for keyword in ["más", "información", "dev"]
                    ):
                        button = btn
                        logger.debug(f"Found developer button by text: {btn_text}")
                        break

            if button:
                await button.click()
                logger.debug("Clicked developer button")

                # Wait for modal to appear
                modal_selectors = [
                    '[role="dialog"]',
                    ".modal, .modal-content",
                    "[class*='modal']",
                    "[class*='offcanvas']",
                ]

                for selector in modal_selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=3000, state="visible")
                        logger.debug(f"Modal appeared with selector: {selector}")
                        return True
                    except:
                        pass

        except Exception as e:
            logger.debug(f"Error opening developer modal: {e}")

        return False

    async def _extract_field_from_modal(self, field_name: str) -> Optional[str]:
        """Extract a field value from inside the modal."""
        try:
            # Look for label-value pattern
            label = await self.page.query_selector(
                f"label:has-text('{field_name}'), strong:has-text('{field_name}')"
            )
            if label:
                # Try to get next element or sibling
                value_elem = await label.evaluate(
                    "el => el.nextElementSibling?.textContent || el.parentElement?.querySelector('[class*=\"value\"]')?.textContent"
                )
                if value_elem:
                    return value_elem.strip()
        except Exception as e:
            logger.debug(f"Error extracting field '{field_name}' from modal: {e}")

        return None

    async def _extract_logo_url(self) -> Optional[str]:
        """Extract company logo URL from modal."""
        try:
            img = await self.page.query_selector("[class*='modal'] img, [role='dialog'] img")
            if img:
                src = await img.get_attribute("src")
                return src
        except Exception as e:
            logger.debug(f"Error extracting logo: {e}")

        return None

    async def _close_developer_modal(self) -> None:
        """Close the developer modal if open."""
        try:
            # Try to find close button
            close_button = await self.page.query_selector(
                "[role='dialog'] button[aria-label='Close'], "
                ".modal-close, "
                "button:has-text('Cerrar')"
            )

            if close_button:
                await close_button.click()
                logger.debug("Closed developer modal")
            else:
                # Try pressing Escape
                await self.page.press("Escape")
                logger.debug("Closed modal with Escape key")
        except Exception as e:
            logger.debug(f"Error closing modal: {e}")

    async def _extract_developer_name(self) -> Optional[str]:
        """Extract developer name from page (direct extraction)."""
        try:
            # Look for developer field
            text = await self.page.text_content()
            # This is a fallback - real extraction would need more context
            return None
        except:
            return None

    async def _extract_email(self) -> Optional[str]:
        """Extract email from page."""
        try:
            # Look for email pattern
            links = await self.page.query_selector_all("a[href^='mailto:']")
            if links:
                href = await links[0].get_attribute("href")
                if href:
                    return href.replace("mailto:", "").split("?")[0]
        except Exception as e:
            logger.debug(f"Error extracting email: {e}")

        return None

    async def _extract_phone(self) -> Optional[str]:
        """Extract phone number from page."""
        try:
            # Look for phone pattern
            links = await self.page.query_selector_all("a[href^='tel:']")
            if links:
                href = await links[0].get_attribute("href")
                if href:
                    return href.replace("tel:", "")
        except Exception as e:
            logger.debug(f"Error extracting phone: {e}")

        return None

    async def extract_summary(self) -> str:
        """Get human-readable summary of extracted developer info."""
        dev_info = await self.extract_all()

        if not dev_info:
            return "👨‍💼 Developer Info: Not found"

        summary = ["👨‍💼 Developer Information:"]

        for key, value in dev_info.items():
            if value and key != "modal_found":
                display_key = key.replace("_", " ").title()
                summary.append(f"  • {display_key}: {str(value)[:50]}")

        return "\n".join(summary)
