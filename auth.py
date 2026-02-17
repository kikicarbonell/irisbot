"""auth.py — Iris authentication handling.

Encapsulates login logic for easy testing and reuse.
"""

import logging

from playwright.async_api import Page, TimeoutError

from config import IRIS_EMAIL, IRIS_PASSWORD, PLAYWRIGHT_TIMEOUT_MS
from iris_selectors import LOGIN_EMAIL_INPUT, LOGIN_PASSWORD_INPUT, LOGIN_SUBMIT_BUTTON

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
        await submit_button.click()

        # Wait for post-login redirect
        # First, try to wait for URL change immediately
        try:
            await page.wait_for_url(
                lambda u: "/iniciar-sesion" not in u.lower(),
                timeout=30000,  # 30s for redirect to occur
            )
            logger.info(f"✓ Redirect detected: {page.url}")
        except TimeoutError:
            # If not redirected, check current URL in case it already changed
            current_url = page.url
            if "/iniciar-sesion" not in current_url.lower():
                logger.info(f"✓ Redirect already occurred: {current_url}")
            else:
                logger.warning(f"⚠ Timeout waiting for redirect. Current URL: {current_url}")
                logger.error("❌ No URL change after login")
                return False

        # Wait for login processing
        try:
            await page.wait_for_load_state("networkidle", timeout=PLAYWRIGHT_TIMEOUT_MS)
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
