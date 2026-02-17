"""config.py — Constants and configuration loading for Iris scraper.

All configuration is managed through environment variables that can be set in a `.env`
file at the project root or directly in your system environment.

Configuration categories:
- Authentication: IRIS_EMAIL, IRIS_PASSWORD (required)
- Browser settings: PLAYWRIGHT_HEADLESS, PLAYWRIGHT_TIMEOUT_MS
- Performance tuning: POLL_INTERVAL_MS, SCROLL_STEP_DELAY_MS, etc.
- Database: DB_FILENAME, DB_DSN
- Platform URLs: IRIS_BASE_URL, IRIS_LOGIN_URL, IRIS_CATALOG_URL

For complete documentation of all options, see: .ai/context/CONFIGURATION.md

Security:
- Do not place credentials in this file in public repositories
- Use environment variables or a `.env` file (which is in .gitignore)
"""

import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

# Iris credentials (Email and Password for authentication)
IRIS_EMAIL: Final[str] = os.getenv("IRIS_EMAIL", "")
IRIS_PASSWORD: Final[str] = os.getenv("IRIS_PASSWORD", "")

# Project
PROJECT_NAME: Final[str] = os.getenv("PROJECT_NAME", "irisbot")
BASE_DIR: Final[Path] = Path(os.getenv("BASE_DIR", Path.cwd())).resolve()
DATA_DIR: Final[Path] = BASE_DIR / "data" / PROJECT_NAME

# Database (SQLite)
DB_FILENAME: Final[str] = os.getenv("DB_FILENAME", "irisbot.db")
DB_PATH: Final[Path] = BASE_DIR / DB_FILENAME
# SQLModel / SQLAlchemy DSN
DB_DSN: Final[str] = os.getenv("DB_DSN", f"sqlite:///{DB_PATH}")

# Playwright / Browser
PLAYWRIGHT_HEADLESS: Final[bool] = os.getenv("PLAYWRIGHT_HEADLESS", "1") not in (
    "0",
    "false",
    "False",
)
PLAYWRIGHT_TIMEOUT_MS: Final[int] = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000"))

# Authentication timeouts (separate from scraping - login needs more time for redirects)
AUTH_BUTTON_CLICK_DELAY_MS: Final[int] = int(
    os.getenv("AUTH_BUTTON_CLICK_DELAY_MS", "2000")
)  # Delay after clicking login
AUTH_REDIRECT_TIMEOUT_MS: Final[int] = int(
    os.getenv("AUTH_REDIRECT_TIMEOUT_MS", "45000")
)  # Wait for URL redirect (45s)
AUTH_NETWORKIDLE_TIMEOUT_MS: Final[int] = int(
    os.getenv("AUTH_NETWORKIDLE_TIMEOUT_MS", "45000")
)  # Wait for page load (45s)

# Pagination timeouts (optimized - shorter than general timeout)
PAGINATION_LOAD_TIMEOUT_MS: Final[int] = int(
    os.getenv("PAGINATION_LOAD_TIMEOUT_MS", "10000")
)  # 10s for loading
PAGINATION_VISIBILITY_TIMEOUT_MS: Final[int] = int(
    os.getenv("PAGINATION_VISIBILITY_TIMEOUT_MS", "3000")
)  # 3s to find button

# Scraper wait times (CONSERVATIVE defaults for maximum reliability)
# These values prioritize stability over speed. Reduce cautiously if needed.
# Polling and detection
POLL_INTERVAL_MS: Final[int] = int(
    os.getenv("POLL_INTERVAL_MS", "300")
)  # Wait between polls for new content
POLL_MAX_ATTEMPTS: Final[int] = int(
    os.getenv("POLL_MAX_ATTEMPTS", "20")
)  # Max polling attempts (20 × 300ms = 6s)

# Scrolling delays
SCROLL_STEP_DELAY_MS: Final[int] = int(
    os.getenv("SCROLL_STEP_DELAY_MS", "300")
)  # Delay between scroll steps
SCROLL_AFTER_DELAY_MS: Final[int] = int(
    os.getenv("SCROLL_AFTER_DELAY_MS", "500")
)  # Delay after scroll operation

# Fallback and retry delays
NETWORKIDLE_FALLBACK_MS: Final[int] = int(
    os.getenv("NETWORKIDLE_FALLBACK_MS", "1500")
)  # Fallback if networkidle fails
SCROLL_RETRY_DELAY_MS: Final[int] = int(
    os.getenv("SCROLL_RETRY_DELAY_MS", "800")
)  # Delay before scroll retry
VIEW_SWITCH_DELAY_MS: Final[int] = int(
    os.getenv("VIEW_SWITCH_DELAY_MS", "300")
)  # Delay after switching views

# Networking / Downloads
CONCURRENT_DOWNLOADS: Final[int] = int(os.getenv("CONCURRENT_DOWNLOADS", "5"))
DOWNLOAD_TIMEOUT_S: Final[int] = int(os.getenv("DOWNLOAD_TIMEOUT_S", "60"))
USER_AGENT: Final[str] = os.getenv("USER_AGENT", "irisbot/1.0 (+https://example.com)")

# Retry & limits
REQUEST_RETRY_COUNT: Final[int] = int(os.getenv("REQUEST_RETRY_COUNT", "3"))
REQUEST_RETRY_BACKOFF_S: Final[float] = float(os.getenv("REQUEST_RETRY_BACKOFF_S", "1.5"))

# Iris URLs
IRIS_BASE_URL: Final[str] = os.getenv("IRIS_BASE_URL", "https://iris.infocasas.com.uy")
IRIS_LOGIN_URL: Final[str] = os.getenv("IRIS_LOGIN_URL", f"{IRIS_BASE_URL}/iniciar-sesion")
IRIS_CATALOG_URL: Final[str] = os.getenv(
    "IRIS_CATALOG_URL", f"{IRIS_BASE_URL}/proyectos?country=1&order=promos%2Cpopularity"
)

# Logging
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")


def ensure_dirs() -> None:
    """Create required directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print(f"Data dir: {DATA_DIR}")
    print(f"DB dsn: {DB_DSN}")
