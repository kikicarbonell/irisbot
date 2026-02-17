"""auth.py — Iris authentication handling.

Encapsulates login logic for easy testing and reuse.
"""

import logging

from playwright.async_api import Page, TimeoutError

from config import (
    AUTH_BUTTON_CLICK_DELAY_MS,
    AUTH_NETWORKIDLE_TIMEOUT_MS,
    AUTH_REDIRECT_TIMEOUT_MS,
    IRIS_EMAIL,
    IRIS_PASSWORD,
    PLAYWRIGHT_TIMEOUT_MS,
)
from iris_selectors import LOGIN_EMAIL_INPUT, LOGIN_PASSWORD_INPUT

logger = logging.getLogger(__name__)


async def authenticate(page: Page, email: str | None = None, password: str | None = None) -> bool:
    """Authenticates in Iris using email and password.

    Args:
        page: Authenticated Playwright page
        email: User email (uses IRIS_EMAIL from config if not provided)
        password: Password (uses IRIS_PASSWORD from config if not provided)

    Returns:
        True if authentication was successful, False otherwise
    """
    email = email or IRIS_EMAIL
    password = password or IRIS_PASSWORD

    if not email or not password:
        logger.error("❌ Email and/or password not configured")
        return False

    try:
        logger.info(f"🔐 Authenticating with email: {email}")

        # Wait for email field to appear
        email_input = page.locator(LOGIN_EMAIL_INPUT)
        await email_input.wait_for(timeout=PLAYWRIGHT_TIMEOUT_MS)
        logger.info("✓ Email field found")

        # Fill email
        await email_input.fill(email)
        logger.info("✓ Email entered")

        # Fill password
        password_input = page.locator(LOGIN_PASSWORD_INPUT)
        await password_input.wait_for(timeout=PLAYWRIGHT_TIMEOUT_MS)
        await password_input.fill(password)
        logger.info("✓ Password entered")

        # Click login button
        # Use specific selector for submit button, not .first() which could pick another
        submit_button = page.locator("button[type='submit']")
        await submit_button.wait_for(timeout=PLAYWRIGHT_TIMEOUT_MS)
        logger.info("✓ Login button found, pressing...")

        # Take screenshot before click for debugging
        await page.screenshot(path="data/debug_login_before_click.png")
        logger.debug("📸 Screenshot taken: debug_login_before_click.png")

        await submit_button.click()
        logger.info("✓ Login button clicked")

        # Give the page time to process the login before checking for redirect
        await page.wait_for_timeout(AUTH_BUTTON_CLICK_DELAY_MS)
        logger.info(f"⏳ Waiting {AUTH_BUTTON_CLICK_DELAY_MS}ms for login to process...")

        # Take screenshot after click to see what happened
        await page.screenshot(path="data/debug_login_after_click.png")
        logger.debug("📸 Screenshot taken: debug_login_after_click.png")

        # Check for error messages on the page
        error_selectors = [
            ".alert-danger",
            ".error-message",
            "[role='alert']",
            ".text-danger",
            ".invalid-feedback",
        ]
        for selector in error_selectors:
            try:
                error_elem = page.locator(selector).first
                count = await error_elem.count()
                if count > 0:
                    error_text = await error_elem.text_content()
                    if error_text and error_text.strip():
                        logger.error(f"❌ Error message on page: {error_text.strip()}")
            except (TypeError, AttributeError):
                # Skip if locator doesn't support count() (e.g., in tests)
                pass

        # Wait for post-login redirect
        # First, try to wait for URL change immediately
        try:
            await page.wait_for_url(
                lambda u: "/iniciar-sesion" not in u.lower(),
                timeout=AUTH_REDIRECT_TIMEOUT_MS,
            )
            logger.info(f"✓ Redirect detected: {page.url}")
        except TimeoutError:
            # If not redirected, check current URL in case it already changed
            current_url = page.url
            if "/iniciar-sesion" not in current_url.lower():
                logger.info(f"✓ Redirect already occurred: {current_url}")
            else:
                logger.warning(f"⚠ Timeout waiting for redirect. Current URL: {current_url}")

                # Take final screenshot for debugging
                await page.screenshot(path="data/debug_login_timeout.png")
                logger.error("📸 Screenshot saved: debug_login_timeout.png")

                # Check page title for clues
                page_title = await page.title()
                logger.error(f"📄 Page title: {page_title}")

                logger.error("❌ No URL change after login")
                logger.error("💡 Check screenshots in data/ folder to diagnose the issue")
                return False

        # Wait for login processing with authentication-specific timeout
        try:
            await page.wait_for_load_state("networkidle", timeout=AUTH_NETWORKIDLE_TIMEOUT_MS)
            logger.info("✓ Page loaded after login")
        except TimeoutError:
            logger.warning("⚠ Timeout esperando carga de página (pero podría estar autenticado)")

        # Validate login was successful (should be in /proyectos)
        current_url = page.url
        logger.info(f"📍 Current URL after login: {current_url}")

        if "/iniciar-sesion" in current_url or "/login" in current_url.lower():
            logger.error(f"❌ Still on login page: {current_url}")
            return False

        if "/proyectos" not in current_url:
            logger.warning(f"⚠ Login apparent but not in /proyectos: {current_url}")
            # Try to navigate to /proyectos directly
            try:
                await page.goto(
                    "https://iris.infocasas.com.uy/proyectos?country=1&order=promos%2Cpopularity",
                    wait_until="domcontentloaded",
                )
                logger.info("✓ Manually navigated to /proyectos")
            except Exception as e:
                logger.warning(f"No se pudo navegar a /proyectos: {e}")

        logger.info(f"✓ Authentication successful. Current URL: {page.url}")
        return True

    except TimeoutError as e:
        logger.error(f"❌ Timeout durante autenticación: {e}")
        return False
    except Exception as e:
        logger.exception(f"❌ Error durante autenticación: {e}")
        return False
