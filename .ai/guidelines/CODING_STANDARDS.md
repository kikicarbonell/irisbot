# CODING STANDARDS - Irisbot

## 🎯 Purpose
This document defines coding conventions, patterns, and best practices for the Irisbot project to ensure consistency, maintainability, and reliability.

---

## 🐍 Python Style Guide

### General Rules
- **Follow PEP 8** - Standard Python style guide
- **Use 4 spaces** for indentation (no tabs)
- **Max line length:** 100 characters (soft limit, 120 hard limit)
- **UTF-8 encoding** for all source files

### Naming Conventions
```python
# Modules: lowercase with underscores
src/scrape_catalog_phase1.py
src/iris_selectors.py

# Classes: PascalCase
class ProjectScraper:
    pass

# Functions/methods: snake_case
async def scrape_catalog():
    pass

# Constants: UPPER_CASE
IRIS_BASE_URL = "https://iris.infocasas.com.uy"
PLAYWRIGHT_TIMEOUT_MS = 30000

# Private members: prefix with underscore
def _internal_helper():
    pass

# Variables: snake_case
project_count = 129
detail_url = "/proyecto/235"
```

### Import Organization
```python
# Standard library imports first
import asyncio
import logging
from pathlib import Path

# Third-party imports second
import playwright
from playwright.async_api import Page, Browser
from dotenv import load_dotenv

# Local application imports third
from auth import authenticate
from config import IRIS_CATALOG_URL
from iris_selectors import PROJECT_CARD_LINK
```

### Type Hints
Use type hints for function signatures:
```python
# Good ✅
async def authenticate(page: Page, email: str = None, password: str = None) -> bool:
    pass

def parse_price(price_text: str) -> float:
    pass

# Bad ❌
async def authenticate(page, email=None, password=None):
    pass
```

---

## 🔄 Async/Await Patterns

### Always Use Async for Playwright
```python
# Good ✅
async def scrape_page(page: Page):
    await page.goto(url)
    element = await page.query_selector("div")
    await element.click()

# Bad ❌ (blocking operations)
def scrape_page(page: Page):
    page.goto(url)  # Missing await
```

### Context Managers for Resources
```python
# Good ✅
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    try:
        # ... scraping logic
    finally:
        await browser.close()

# Bad ❌ (no cleanup)
p = async_playwright()
browser = await p.chromium.launch()
page = await browser.new_page()
# ... forgot to close
```

---

## 🗄️ Database Patterns

### Always Use Context Managers
```python
# Good ✅
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    return cursor.fetchall()

# Bad ❌
conn = get_connection()
cursor = conn.cursor()
cursor.execute("...")
# ... forgot to close connection
```

### Use Parameterized Queries
```python
# Good ✅ (SQL injection safe)
cursor.execute(
    "INSERT INTO projects (name, zone) VALUES (?, ?)",
    (project_name, project_zone)
)

# Bad ❌ (SQL injection vulnerable)
cursor.execute(f"INSERT INTO projects (name) VALUES ('{project_name}')")
```

### INSERT OR IGNORE for Duplicates
```python
# Good ✅ (handles duplicates gracefully)
cursor.execute(
    "INSERT OR IGNORE INTO projects (detail_url, name) VALUES (?, ?)",
    (url, name)
)

# Bad ❌ (crashes on duplicate)
cursor.execute("INSERT INTO projects ...")  # Will fail if url exists
```

---

## 🎣 Playwright Scraping Patterns

### Selector Hierarchy (Prefer in Order)
1. **ID selectors** (fastest, most reliable)
   ```python
   await page.query_selector('#project-title')
   ```

2. **Data attributes** (semantic, stable)
   ```python
   await page.query_selector('[data-testid="project-card"]')
   ```

3. **CSS classes** (less stable, but common)
   ```python
   await page.query_selector('.project-card')
   ```

4. **Text matching** (fragile, last resort)
   ```python
   await page.query_selector('button:has-text("Cargar más")')
   ```

### Wait Strategies

**Use Auto-Wait When Possible:**
```python
# Good ✅ (Playwright auto-waits for element)
await page.click('button#submit')
```

**Explicit Waits for Dynamic Content:**
```python
# Good ✅ (wait for selector before interacting)
await page.wait_for_selector('div.project-card', state='visible')
element = await page.query_selector('div.project-card')

# Good ✅ (wait for network idle after navigation)
await page.goto(url, wait_until='networkidle')
```

**Polling for Dynamic Updates:**
```python
# Good ✅ (custom polling for AJAX updates)
for attempt in range(20):  # 20 * 500ms = 10s
    await page.wait_for_timeout(500)
    result = await page.evaluate("""
        () => document.querySelectorAll('a[href*="/proyecto/"]').length
    """)
    if result > prev_count:
        return True
return False
```

### Error Handling
```python
# Good ✅
try:
    await page.click('button', timeout=5000)
except playwright.async_api.TimeoutError:
    logging.warning("Button not found, continuing...")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    raise

# Bad ❌ (bare except)
try:
    await page.click('button')
except:
    pass  # Silent failure
```

---

## 📝 Logging Standards

### Use Structured Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Usage
logger.info(f"Scraped {project_count} projects")
logger.warning(f"Failed to load project {project_id}")
logger.error(f"Database error: {e}", exc_info=True)
```

### Log Levels
- **DEBUG:** Detailed diagnostic info (selector matches, DOM state)
- **INFO:** General progress updates (N projects scraped)
- **WARNING:** Recoverable issues (element not found, retry)
- **ERROR:** Errors that prevent specific operations
- **CRITICAL:** System-level failures (DB connection lost)

---

## 🧪 Testing Standards

### Test File Organization
```
tests/
    test_config.py          # Unit tests for config.py
    test_database.py        # Unit tests for database.py
    test_auth.py            # Integration tests for auth.py
    test_scraper_flow.py    # End-to-end integration tests
    conftest.py             # Shared pytest fixtures
```

### Fixture Pattern
```python
# conftest.py
import pytest

@pytest.fixture
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        yield browser
        await browser.close()

@pytest.fixture
def db_connection():
    conn = get_connection()
    yield conn
    conn.close()
```

### Test Naming
```python
# Good ✅
def test_authenticate_with_valid_credentials():
    pass

def test_parse_price_with_usd_symbol():
    pass

# Bad ❌
def test1():
    pass

def test_stuff():
    pass
```

### Assertions
```python
# Good ✅ (descriptive)
assert project_count == 129, f"Expected 129 projects, got {project_count}"

# Good ✅ (pytest matchers)
assert "proyecto" in detail_url

# Bad ❌ (no message)
assert project_count == 129
```

---

## 🔧 Configuration Management

### Environment Variables
- **NEVER commit `.env` to git**
- Always provide `.env.example` template
- Validate required vars on startup

```python
# Good ✅
from dotenv import load_dotenv
import os

load_dotenv()

IRIS_EMAIL = os.getenv("IRIS_EMAIL")
if not IRIS_EMAIL:
    raise ValueError("IRIS_EMAIL environment variable not set")

# Bad ❌
IRIS_EMAIL = "hardcoded@example.com"
```

### Configuration Hierarchy
1. Environment variables (.env)
2. Default constants (src/config.py)
3. Command-line arguments (future)

---

## 📦 Module Organization

### Single Responsibility Principle
Each module should have ONE clear purpose:

```
src/auth.py           → Authentication only
src/database.py       → Schema definition only
src/db_manager.py     → Database operations only
src/iris_selectors.py → Selector constants only
src/utils.py          → Generic helpers only (parsing, formatting)
src/downloader.py     → File download operations only (use aiohttp for async downloads)
```

### File Storage Structure
Downloaded assets should follow this structure:
```
./data/{project_name}/{unit_number}/
  ├── brochure.pdf
  ├── floor_plan.pdf
  └── images/
      ├── image_1.jpg
      └── image_2.jpg
```

### Avoid Circular Imports
```python
# Bad ❌
# auth.py imports scraper.py
# scraper.py imports auth.py
# → Circular dependency

# Good ✅
# Both import shared src/config.py or src/constants.py
```

---

## 🚨 Error Handling Philosophy

### Fail Fast for Critical Errors
```python
# Good ✅ (authentication failure should stop scraping)
if not await authenticate(page):
    raise AuthenticationError("Failed to authenticate")
```

### Graceful Degradation for Non-Critical Errors
```python
# Good ✅ (missing image URL shouldn't stop scraping)
try:
    image_url = await card.get_attribute('img', 'src')
except Exception:
    image_url = None  # Continue with None
```

### Log Then Re-Raise
```python
# Good ✅
try:
    await page.goto(url)
except Exception as e:
    logger.error(f"Failed to navigate to {url}: {e}")
    raise  # Let caller handle
```

---

## 📐 Code Organization Patterns

### Extract Magic Numbers
```python
# Bad ❌
for attempt in range(20):
    await page.wait_for_timeout(500)

# Good ✅
MAX_POLL_ATTEMPTS = 20
POLL_INTERVAL_MS = 500

for attempt in range(MAX_POLL_ATTEMPTS):
    await page.wait_for_timeout(POLL_INTERVAL_MS)
```

### Use Descriptive Variable Names
```python
# Bad ❌
x = await page.query_selector_all('a')
for i in x:
    y = await i.get_attribute('href')

# Good ✅
project_links = await page.query_selector_all('a[href*="/proyecto/"]')
for link in project_links:
    detail_url = await link.get_attribute('href')
```

### Early Returns
```python
# Good ✅ (reduce nesting)
async def scrape_project(project_id):
    if not project_id:
        return None

    project = get_project_from_db(project_id)
    if not project:
        return None

    return await scrape_details(project)

# Bad ❌ (deep nesting)
async def scrape_project(project_id):
    if project_id:
        project = get_project_from_db(project_id)
        if project:
            return await scrape_details(project)
    return None
```

---

## 🔒 Security Best Practices

### Never Log Credentials
```python
# Bad ❌
logger.info(f"Logging in with {email}:{password}")

# Good ✅
logger.info(f"Logging in as {email}")
```

### Never Hardcode Credentials
```python
# Bad ❌
IRIS_EMAIL = "user@example.com"
IRIS_PASSWORD = "mypassword"

# Good ✅
from dotenv import load_dotenv
import os

load_dotenv()
IRIS_EMAIL = os.getenv("IRIS_EMAIL")
IRIS_PASSWORD = os.getenv("IRIS_PASSWORD")

if not IRIS_EMAIL or not IRIS_PASSWORD:
    raise ValueError("Missing required environment variables")
```

### Sanitize User Inputs
```python
# Good ✅
def safe_filename(text: str) -> str:
    """Remove unsafe characters from filename"""
    return re.sub(r'[^\w\s-]', '', text).strip()
```

### Use HTTPS URLs
```python
# Good ✅
IRIS_BASE_URL = "https://iris.infocasas.com.uy"

# Bad ❌
IRIS_BASE_URL = "http://iris.infocasas.com.uy"  # Insecure
```

---

## 📋 Documentation Standards

### Docstrings (Google Style)
```python
def parse_price(price_text: str) -> float:
    """
    Parse price string to float.

    Args:
        price_text: Price string like "USD 120.000" or "U$S 125000"

    Returns:
        Float value without currency symbols (e.g., 120000.0)

    Raises:
        ValueError: If price_text cannot be parsed

    Examples:
        >>> parse_price("USD 120.000")
        120000.0
        >>> parse_price("U$S 125.500")
        125500.0
    """
    pass
```

### Inline Comments
```python
# Good ✅ (explain WHY, not WHAT)
# Poll instead of wait_for_function because Iris has slow AJAX updates
for attempt in range(20):
    await page.wait_for_timeout(500)

# Bad ❌ (restates code)
# Loop 20 times
for attempt in range(20):
    pass
```

---

## 🚫 Project Constraints

### Technology Restrictions
- ❌ **NO Selenium** - Use Playwright exclusively for browser automation
- ❌ **NO synchronous HTTP libraries** - Use `aiohttp` for file downloads, not `requests`
- ❌ **NO blocking I/O** - All network and disk operations must be async
- ❌ **NO hardcoded paths** - Use `pathlib` for cross-platform compatibility

### Resilience Requirements
- ✅ **Graceful degradation**: If a CSS selector fails, log warning and continue to next item
- ✅ **Retry logic**: Network operations should retry with exponential backoff (3 attempts)
- ✅ **Error isolation**: One failed unit should not stop the entire scraping process

```python
# Good ✅ (continues on selector failure)
try:
    price = await page.query_selector('span.price')
    if price:
        price_text = await price.text_content()
    else:
        logger.warning("Price selector not found, setting to None")
        price_text = None
except Exception as e:
    logger.error(f"Error extracting price: {e}")
    price_text = None
# Continue with next field

# Bad ❌ (crashes entire scraper)
price = await page.query_selector('span.price')  # Raises if not found
price_text = await price.text_content()
```

---

## 🔍 Code Review Checklist

Before committing code, verify:
- [ ] Follows PEP 8 style guide
- [ ] Has type hints on function signatures
- [ ] Uses async/await correctly (no sync operations)
- [ ] Uses Playwright (NOT Selenium)
- [ ] Uses aiohttp for downloads (NOT requests)
- [ ] Has proper error handling with graceful degradation
- [ ] Logs important actions
- [ ] No hardcoded credentials
- [ ] No hardcoded file paths (uses pathlib)
- [ ] Has docstrings for public functions
- [ ] Passes all tests (`pytest`)
- [ ] No unnecessary debug prints
- [ ] Imports are organized
- [ ] Variables have descriptive names

---

**Última actualización:** Febrero 16, 2026
