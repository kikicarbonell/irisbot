# SCRAPING RULES - Irisbot

## 🎯 Purpose
This document defines scraping-specific rules, patterns, and best practices for extracting data from the Iris PropertyTech platform.

---

## 🌐 Target Site: Iris PropertyTech

### Site Characteristics
- **URL:** https://iris.infocasas.com.uy
- **Architecture:** Single Page Application (SPA) - React/Vue
- **Authentication:** Required (email/password)
- **Rendering:** Client-side JavaScript (requires browser automation)
- **Pagination:** Dynamic loading via "Cargar más" button
- **Rate Limiting:** Unknown (be conservative)

### Ethical Scraping Guidelines
1. **Respect robots.txt** (if present)
2. **Authenticate legitimately** (use valid credentials)
3. **Rate limit requests** (don't overwhelm servers)
4. **Scrape during off-peak hours** (avoid business hours)
5. **Cache results** (don't re-scrape unnecessarily)
6. **Identify your scraper** (custom User-Agent if needed)

---

## 🔐 Authentication Rules

### Login Process
```python
async def authenticate(page: Page, email: str, password: str) -> bool:
    """
    Steps:
    1. Navigate to /iniciar-sesion
    2. Wait for email input (30s timeout)
    3. Fill email and password
    4. Click submit button
    5. Wait for redirect to /feed or /proyectos
    6. Return True if successful
    """
```

### Session Management
- **Session type:** Cookie-based (managed by Playwright)
- **Session duration:** ~24 hours (estimated)
- **Re-authentication:** Required if session expires
- **Detection:** If redirected to `/iniciar-sesion`, re-authenticate

### Credentials
```python
# Always load from environment
IRIS_EMAIL = os.getenv("IRIS_EMAIL")
IRIS_PASSWORD = os.getenv("IRIS_PASSWORD")

# Validate before scraping
if not IRIS_EMAIL or not IRIS_PASSWORD:
    raise ValueError("Missing IRIS_EMAIL or IRIS_PASSWORD")
```

---

## 🎣 CSS Selector Rules

### Selector Priority (Most Stable → Least Stable)
1. **Unique IDs** (if available) - `#project-title`
2. **Data attributes** - `[data-testid="project-card"]`
3. **Semantic classes** - `.project-card`, `.unit-table`
4. **Structural selectors** - `a[href*='/proyecto/']`
5. **Text matching** (last resort) - `button:has-text("Cargar más")`

### Selector Validation
Before using a selector in production:
```python
# 1. Test on 3+ different pages
# 2. Verify it returns expected count
# 3. Check for false positives

selector = "a[href*='/proyecto/']"
elements = await page.query_selector_all(selector)
assert len(elements) > 0, f"Selector {selector} returned 0 elements"
```

### Selector Centralization
**ALWAYS define selectors in `src/iris_selectors.py`:**
```python
# Good ✅
from iris_selectors import PROJECT_CARD_LINK
cards = await page.query_selector_all(PROJECT_CARD_LINK)

# Bad ❌
cards = await page.query_selector_all("a[href*='/proyecto/']")
```

### Known Selectors

#### Authentication Page
```python
LOGIN_EMAIL_INPUT = "input[type='email'], input[name*='email' i]"
LOGIN_PASSWORD_INPUT = "input[type='password']"
LOGIN_SUBMIT_BUTTON = "button[type='submit']"
```

#### Catalog Page (Phase 1)
```python
PROJECT_CARD_CONTAINER = "div.gx-2.gy-3.mb-4.mt-1.mt-lg-0.row"
PROJECT_CARD_LINK = "a[href*='/proyecto/']"
LOAD_MORE_BUTTON = "button:has-text('Cargar más')"
```

#### Project Detail Page (Phase 2)
```python
# To be defined after DOM inspection
PROJECT_TITLE = "h1.project-title"  # Placeholder
PROJECT_DESCRIPTION = "div.project-description"  # Placeholder
UNITS_TABLE = "table.units-table"  # Placeholder
DEVELOPER_INFO_BUTTON = "button:has-text('Más información')"  # Confirmed
```

---

## ⏱️ Wait Strategies

### Rule 1: Always Wait for Critical Elements
```python
# Good ✅
await page.wait_for_selector('div.project-card', state='visible', timeout=30000)
cards = await page.query_selector_all('div.project-card')

# Bad ❌
cards = await page.query_selector_all('div.project-card')  # Might be empty if not loaded
```

### Rule 2: Use `networkidle` for Initial Page Loads
```python
# Good ✅ (wait for all AJAX to complete)
await page.goto(url, wait_until='networkidle')

# Acceptable ✅ (faster, but may miss late-loading content)
await page.goto(url, wait_until='domcontentloaded')
```

### Rule 3: Poll for Dynamic Updates
When content updates via AJAX without new network requests:
```python
# Good ✅ (custom polling)
async def wait_for_more_projects(page, prev_count):
    MAX_ATTEMPTS = 20
    POLL_INTERVAL_MS = 500

    for attempt in range(MAX_ATTEMPTS):
        await page.wait_for_timeout(POLL_INTERVAL_MS)
        current_count = await page.evaluate("""
            () => document.querySelectorAll('a[href*="/proyecto/"]').length
        """)
        if current_count > prev_count:
            return True
    return False

# Bad ❌ (wait_for_function can timeout unexpectedly)
await page.wait_for_function(
    "document.querySelectorAll('a[href*=\"/proyecto/\"]').length > prev_count",
    timeout=10000
)
```

### Rule 4: Timeout Values
```python
# Critical actions (authentication, initial page load)
CRITICAL_TIMEOUT_MS = 30000  # 30s

# Normal actions (click button, wait for selector)
NORMAL_TIMEOUT_MS = 10000  # 10s

# Polling intervals
POLL_INTERVAL_MS = 500  # 500ms

# Fast checks (element existence)
FAST_TIMEOUT_MS = 3000  # 3s
```

---

## 📄 Pagination Patterns

### "Cargar más" Button Pattern (Catalog)
```python
async def handle_pagination(page: Page):
    """
    Iris catalog uses 'Load More' button that:
    1. Appends 12 new projects to existing list
    2. Updates DOM without page reload
    3. Hides button when no more projects

    Strategy:
    - Count projects before click
    - Click button
    - Poll until count increases OR timeout
    - Repeat until button disappears or no new projects
    """
    iteration = 1

    while True:
        # Count before
        prev_hrefs = await page.evaluate("""
            () => Array.from(
                document.querySelectorAll('a[href*="/proyecto/"]')
            ).map(a => a.href)
        """)

        # Find button
        button = await page.query_selector(LOAD_MORE_BUTTON)
        if not button:
            break

        # Click
        await button.scroll_into_view_if_needed()
        await button.click()

        # Wait for new content
        success = await wait_for_more_projects(page, prev_hrefs)
        if not success:
            break

        iteration += 1
```

### Scroll-Based Pagination (Alternative - Not Used Yet)
Some sites trigger loading on scroll:
```python
# For future reference if Iris changes to infinite scroll
async def scroll_pagination(page: Page):
    prev_height = 0
    while True:
        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        # Check if new content loaded
        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height
```

---

## 🗂️ Data Extraction Patterns

### Rule 1: Extract at Card Level
```python
# Good ✅ (extract from each card independently)
async def extract_project_card_data(card):
    """Extract all fields from a single project card"""
    name = await card.text_content('h3.project-name')
    zone = await card.text_content('span.zone')
    # ... more fields
    return {
        'name': name,
        'zone': zone,
        # ...
    }

# Bad ❌ (extract all at once with page-level selectors)
names = await page.query_selector_all('h3.project-name')
zones = await page.query_selector_all('span.zone')
# Risk: mismatched indices if cards load asynchronously
```

### Rule 2: Handle Missing Fields Gracefully
```python
# Good ✅
try:
    commission = await card.text_content('span.commission')
except Exception:
    commission = None  # Field doesn't exist for this project

# Bad ❌
commission = await card.text_content('span.commission')  # Crashes if missing
```

### Rule 3: Parse Immediately After Extraction
```python
# Good ✅
price_text = await card.text_content('span.price')
price_float = parse_price(price_text)  # Convert "USD 120.000" → 120000.0

# Bad ❌
price_text = await card.text_content('span.price')
# Store as-is in DB, parse later (harder to debug)
```

### Rule 4: Use `get_attribute()` for URLs and Hrefs
```python
# Good ✅
detail_url = await card.get_attribute('href')
image_url = await img_element.get_attribute('src')

# Bad ❌
detail_url = await card.text_content()  # Gets visible text, not href
```

---

## 🔄 Error Recovery Strategies

### Retry on Transient Errors
```python
async def retry_operation(operation, max_attempts=3, delay=2):
    """Retry operation with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return await operation()
        except playwright.async_api.TimeoutError:
            if attempt < max_attempts - 1:
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise
```

### Skip Failed Projects, Continue Scraping
```python
# Good ✅ (don't let one failure stop everything)
for project in projects:
    try:
        await scrape_project_details(project)
    except Exception as e:
        logger.error(f"Failed to scrape {project['name']}: {e}")
        continue  # Move to next project

# Bad ❌
for project in projects:
    await scrape_project_details(project)  # One failure stops all
```

### Log Failed URLs for Manual Review
```python
failed_projects = []

try:
    await scrape_project(url)
except Exception as e:
    failed_projects.append({'url': url, 'error': str(e)})

# Save to file for later retry
with open('failed_projects.json', 'w') as f:
    json.dump(failed_projects, f, indent=2)
```

---

## 📸 Screenshot & Debugging Rules

### When to Take Screenshots
1. **Authentication failure** - Capture login page state
2. **Selector mismatch** - See what page actually looks like
3. **Unexpected layout** - Document for selector updates
4. **Before critical actions** - Verify page state

### Screenshot Naming Convention
```python
# Good ✅
await page.screenshot(path=f"debug/auth_failure_{timestamp}.png")
await page.screenshot(path=f"debug/pagination_iter_{iteration}.png")

# Bad ❌
await page.screenshot(path="screenshot.png")  # Overwrites previous
```

### HTML Snapshots for Deep Debugging
```python
# Save full HTML for post-mortem analysis
html_content = await page.content()
with open(f'debug/page_{timestamp}.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
```

---

## 🚦 Rate Limiting & Politeness

### Respect Server Load
```python
# Add delays between requests
DELAY_BETWEEN_PROJECTS_SEC = 1.0

for project in projects:
    await scrape_project(project)
    await asyncio.sleep(DELAY_BETWEEN_PROJECTS_SEC)
```

### Limit Concurrent Requests (Phase 2)
```python
# Use semaphore to limit parallelism
MAX_CONCURRENT_REQUESTS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def scrape_with_limit(project):
    async with semaphore:
        await scrape_project_details(project)
```

### Detect Rate Limiting
```python
# Watch for rate limit signals
response = await page.goto(url)
if response.status == 429:  # Too Many Requests
    logger.warning("Rate limited, backing off...")
    await asyncio.sleep(60)  # Wait 1 minute
```

---

## 🗃️ Data Validation Rules

### Validate Before Storing
```python
def validate_project_data(data: dict) -> bool:
    """Validate project data before DB insertion"""
    required_fields = ['name', 'detail_url']

    for field in required_fields:
        if not data.get(field):
            return False

    # Validate URL format
    if not data['detail_url'].startswith('/proyecto/'):
        return False

    return True

# Usage
if validate_project_data(project):
    insert_project(conn, project)
else:
    logger.warning(f"Invalid project data: {project}")
```

### Normalize Data Formats
```python
# Prices: Always store as float
price_float = parse_price("USD 120.000")  # → 120000.0

# Booleans: Always store as 0/1
has_ley_vp = 1 if "Ley VP" in text else 0

# URLs: Always store as absolute paths
detail_url = "/proyecto/235"  # ✅
# NOT "proyecto/235" ❌
```

---

## 📋 Phase-Specific Rules

### Phase 1: Catalog Scraping ✅
**Goal:** Extract ALL projects from catalog

**Rules:**
1. Paginate until "Cargar más" disappears
2. Count unique `detail_url` to detect completion
3. Use `INSERT OR IGNORE` for duplicates
4. Log iteration progress (N projects visible, N unique)
5. Take screenshot on final iteration for verification

**Success Criteria:**
- All projects loaded (count matches Iris counter if visible)
- No duplicates in database
- 100% of visible cards extracted

### Phase 2: Detail Scraping 🚧
**Goal:** Extract units + assets for each project

**Rules:**
1. Navigate to each `detail_url` from Phase 1
2. Wait for units table to load (may be AJAX)
3. Extract ALL rows from units table
4. Click "Más información" ONLY if button exists
5. Download assets ONLY if URLs are present
6. Handle projects with 0 units (edge case)
7. Respect rate limits (1-2 sec delay between projects)

**Success Criteria:**
- 100% of projects processed (even if some fail)
- Units table extracted for 95%+ of projects
- Assets downloaded for 80%+ of projects (some may not have PDFs)

---

## 🐛 Common Pitfalls & Solutions

### Pitfall 1: Wrong Selector
**Problem:** `.table-row` selector returns 0 elements
**Solution:** Inspect actual DOM, use `a[href*='/proyecto/']`
**Prevention:** Always test selectors on 3+ sample pages

### Pitfall 2: Race Condition
**Problem:** Clicking button before it's ready
**Solution:** Use `await button.wait_for_element_state('enabled')`
**Prevention:** Use Playwright's auto-wait features

### Pitfall 3: Stale Element Reference
**Problem:** Element removed from DOM after pagination
**Solution:** Re-query elements after DOM updates
**Prevention:** Don't cache element handles across iterations

### Pitfall 4: Timeout on Slow Networks
**Problem:** `wait_for_selector` times out on slow connection
**Solution:** Increase timeout or use polling
**Prevention:** Test on throttled network (Playwright network throttling)

### Pitfall 5: Modal Blocking Click
**Problem:** Clicking button when modal is open
**Solution:** Close modal first or check visibility
**Prevention:** Always verify `is_visible()` before click

---

## 📚 Selector Reference

### Current Working Selectors (Phase 1)
```python
# Login
LOGIN_EMAIL_INPUT = "input[type='email'], input[name*='email' i]"
LOGIN_PASSWORD_INPUT = "input[type='password']"
LOGIN_SUBMIT_BUTTON = "button[type='submit']"

# Catalog
PROJECT_CARD_LINK = "a[href*='/proyecto/']"
LOAD_MORE_BUTTON = "button:has-text('Cargar más')"

# Extraction (within card context)
# Generic approach: use .text_content() on descriptive elements
```

### To Be Documented (Phase 2)
```python
# Project detail page selectors TBD after DOM inspection
# Will be added after analyzing 3-5 sample project pages
```

---

**Última actualización:** Febrero 16, 2026
