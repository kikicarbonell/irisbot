import asyncio
import logging
import os
import sqlite3
import time
from pathlib import Path

from playwright.async_api import async_playwright

from auth import authenticate
from config import (
    IRIS_BASE_URL,
    IRIS_CATALOG_URL,
    IRIS_LOGIN_URL,
    LOG_LEVEL,
    NETWORKIDLE_FALLBACK_MS,
    PAGINATION_LOAD_TIMEOUT_MS,
    PAGINATION_VISIBILITY_TIMEOUT_MS,
    PLAYWRIGHT_HEADLESS,
    PLAYWRIGHT_TIMEOUT_MS,
    POLL_INTERVAL_MS,
    POLL_MAX_ATTEMPTS,
    SCROLL_AFTER_DELAY_MS,
    SCROLL_RETRY_DELAY_MS,
    SCROLL_STEP_DELAY_MS,
    VIEW_SWITCH_DELAY_MS,
)

# Configure logging to show in console
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# URLs are now loaded from config.py (no CLI args needed)
LOGIN_URL = IRIS_LOGIN_URL
CATALOG_URL = IRIS_CATALOG_URL
DB_PATH = Path("catalog_projects.db")

PROJECT_CARD_SELECTORS = [
    "table tbody tr",
    "a[href*='/proyecto/']",
    "div.property-card",
    "article:has(a[href*='/proyecto'])",
    "div:has(a[href*='/proyecto'])",
]

CARGAR_MAS_SELECTORS = [
    "button:has-text('Cargar más')",
    "button:has-text('Mostrar más')",
    "button:has-text('Ver más')",
    "a:has-text('Cargar más')",
    "a:has-text('Mostrar más')",
]

PROJECTS_API_PATH = "get-projects-search"
COLUMN_ROW_SELECTOR = "a[href*='/proyecto/']"  # Updated: projects are links, not .table-row divs
CATALOG_SCROLL_CONTAINER = "div.gx-2.gy-3.mb-4.mt-1.mt-lg-0.row"


OUTPUT_DIR = Path("catalog_artifacts")
MAX_PAGES = int(os.environ.get("CATALOG_MAX_PAGES", "200"))


# --- DB Setup ---
def setup_db():
    """Set up SQLite database with project table schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY,
            detail_url TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            zone TEXT,
            delivery_type TEXT,
            delivery_torres TEXT,
            project_status TEXT,
            price_from TEXT,
            developer TEXT,
            commission TEXT,
            has_ley_vp BOOLEAN DEFAULT 0,
            location TEXT,
            image_url TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Migrate existing DB: drop and recreate to match new schema
    c.execute("PRAGMA table_info(projects)")
    existing = {row[1] for row in c.fetchall()}

    # If old table exists, rename it and create new one
    if (
        "realized_by" in existing
        or "ley_vp" in existing
        or "description" in existing
        or "id" in existing
    ):
        c.execute("DROP TABLE IF EXISTS projects_old")
        c.execute("ALTER TABLE projects RENAME TO projects_old")
        c.execute(
            """
            CREATE TABLE projects (
                project_id INTEGER PRIMARY KEY,
                detail_url TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                zone TEXT,
                delivery_type TEXT,
                delivery_torres TEXT,
                project_status TEXT,
                price_from TEXT,
                developer TEXT,
                commission TEXT,
                has_ley_vp BOOLEAN DEFAULT 0,
                location TEXT,
                image_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

    conn.commit()
    return conn


# --- Extraction ---
async def safe_text(card, selector):
    """Extract text content from element within a card using selector."""
    elem = await card.query_selector(selector)
    if not elem:
        return None
    text = await elem.text_content()
    return text.strip() if text else None


async def safe_attr(card, selector, attr):
    """Extract attribute value from element within a card."""
    if selector:
        elem = await card.query_selector(selector)
        if elem:
            return await elem.get_attribute(attr)
    return await card.get_attribute(attr)


async def safe_text_in_col(row, col_index, selector=None):
    """Extract text from a column by div position within a row."""
    col = await row.query_selector(f":scope > div:nth-child({col_index})")
    if not col:
        return None
    if selector:
        elem = await col.query_selector(selector)
        if not elem:
            return None
        text = await elem.text_content()
        return text.strip() if text else None
    text = await col.text_content()
    return text.strip() if text else None


async def safe_last_text_in_col(row, col_index, selector):
    """Extract last element's text from a column selector."""
    col = await row.query_selector(f":scope > div:nth-child({col_index})")
    if not col:
        return None
    elems = await col.query_selector_all(selector)
    if not elems:
        return None
    text = await elems[-1].text_content()
    return text.strip() if text else None


def parse_delivery_info(delivery_text):
    """Parse delivery column to extract delivery type and project status.

    Extracts:
        - delivery_type: categoría o fecha (INMEDIATA, MES AÑO)
        - delivery_torres: información por torre si existe
        - project_status: estado del proyecto (A estrenar, En construcción, En pozo)

    Returns:
        tuple: (delivery_type, delivery_torres, project_status)
    """
    if not delivery_text:
        return None, None, None

    delivery_text = delivery_text.strip()

    # Detectar estado del proyecto (palabras clave)
    project_status = None
    status_keywords = ["a estrenar", "en construcción", "en pozo"]
    text_lower = delivery_text.lower()
    for keyword in status_keywords:
        if keyword in text_lower:
            project_status = keyword.title()
            break

    # Si contiene "TORRE", parsear como multi-torre
    if "TORRE" in delivery_text.upper():
        # Formato: "TORRE X ESTADO, TORRE Y ESTADO" o similar
        delivery_torres = delivery_text
        # Intentar extraer el delivery_type principal (el primero mencionado)
        parts = delivery_text.split(",")
        delivery_type = parts[0].strip() if parts else delivery_text
    else:
        # Formato simple: solo estado/fecha
        delivery_torres = None
        delivery_type = delivery_text

    return delivery_type, delivery_torres, project_status


async def extract_delivery_and_status_from_column(col):
    """Extract delivery type and project status from delivery column.

    Parses column structure:
        <div class="px-1 col">
            <span class="tag-hand-over">entrega inmediata</span>
            <p class="text-secondary">Estado: A estrenar</p>
        </div>

    Returns:
        tuple: (delivery_type, delivery_torres, project_status)
    """
    if not col:
        return None, None, None

    # Extract delivery type (from tag-hand-over span)
    delivery_elem = await col.query_selector(".tag-hand-over")
    delivery_raw = None
    if delivery_elem:
        delivery_raw = await delivery_elem.text_content()
        delivery_raw = delivery_raw.strip() if delivery_raw else None

    # Extract project status (from text-secondary p tag with "Estado:")
    status_paragraph = await col.query_selector("p.text-secondary")
    project_status = None
    if status_paragraph:
        status_text = await status_paragraph.text_content()
        if status_text and "Estado:" in status_text:
            # Extract text after "Estado:"
            project_status = status_text.split("Estado:")[-1].strip()

    # Parse delivery info to get delivery_torres and delivery_type
    delivery_type, delivery_torres, _ = parse_delivery_info(delivery_raw)

    return delivery_type, delivery_torres, project_status


def parse_ley_vp(ley_vp_text):
    """Parse Ley VP field to boolean.

    Converts "-" or empty value to False, any other content to True.

    Args:
        ley_vp_text: Text value to parse.

    Returns:
        bool: True if has Ley VP, False otherwise.
    """
    if not ley_vp_text:
        return False
    ley_vp_text = ley_vp_text.strip()
    if not ley_vp_text or ley_vp_text == "-":
        return False
    return True


async def extract_ley_vp_from_column(col):
    """Extract Ley VP value from column, checking both text and visual elements.

    Checks for check icon or visual indicator first, then text content.

    Args:
        col: Column element to check.

    Returns:
        bool: True if has Ley VP (icon or content), False if "-" or empty.
    """
    if not col:
        return False

    # First check if there's a check icon or visual indicator (i, svg, etc.)
    icon = await col.query_selector("i, svg, .icon, [class*='check']")
    if icon:
        return True

    # If no icon, check text content
    text = await col.text_content()
    text = text.strip() if text else ""

    # If text is "-" or empty, no Ley VP
    if not text or text == "-":
        return False

    # Any other text content means has Ley VP
    return True


def build_absolute_url(relative_url):
    """Build absolute URL from relative URL using IRIS_BASE_URL.

    Args:
        relative_url: Relative or absolute URL path.

    Returns:
        str: Absolute URL or None if input was None.
    """
    if not relative_url:
        return None
    if relative_url.startswith("http"):
        return relative_url
    if not relative_url.startswith("/"):
        relative_url = "/" + relative_url
    return IRIS_BASE_URL + relative_url


def extract_project_id_from_url(url):
    """Extract numeric project ID from URL.

    Examples:
        "/proyecto/235" -> 235
        "https://iris.infocasas.com.uy/proyecto/682?operation=Venta" -> 682
        "/proyecto/1234/detalle" -> 1234

    Args:
        url: Project URL (absolute or relative)

    Returns:
        int: Project ID or None if not found
    """
    if not url:
        return None

    import re

    # Pattern to match numeric ID after "/proyecto/"
    match = re.search(r"/proyecto/(\d+)", url)
    if match:
        return int(match.group(1))

    return None


def compare_project_data(existing_row, new_data):
    """Compare existing project with new scraped data to detect changes.

    Args:
        existing_row: Tuple from database (project_id, detail_url, name, zone, delivery_type,
                      delivery_torres, project_status, price_from, developer, commission,
                      has_ley_vp, location, image_url, scraped_at, updated_at)
        new_data: Dict with keys: name, zone, delivery_type, delivery_torres, project_status,
                  price_from, developer, commission, has_ley_vp, location, image_url, detail_url

    Returns:
        tuple: (has_changes: bool, changes_dict: dict with changed field names as keys)
    """
    if not existing_row:
        return True, {}

    # Map database columns to new_data keys
    fields_to_check = [
        ("detail_url", 1),
        ("name", 2),
        ("zone", 3),
        ("delivery_type", 4),
        ("delivery_torres", 5),
        ("project_status", 6),
        ("price_from", 7),
        ("developer", 8),
        ("commission", 9),
        ("has_ley_vp", 10),
        ("location", 11),
        ("image_url", 12),
    ]

    changes = {}
    for field_key, db_index in fields_to_check:
        old_value = existing_row[db_index]
        new_value = new_data.get(field_key)

        # For boolean fields, convert to int for comparison if needed
        if field_key == "has_ley_vp":
            new_value = int(new_value) if isinstance(new_value, bool) else new_value
            old_value = int(old_value) if isinstance(old_value, bool) else old_value

        # Compare values (None == None is True)
        if old_value != new_value:
            changes[field_key] = {"old": old_value, "new": new_value}

    has_changes = len(changes) > 0
    return has_changes, changes


def format_change_message(project_id, changes_dict):
    """Format change detection message for logging.

    Args:
        project_id: Project ID
        changes_dict: Dictionary with changed fields

    Returns:
        str: Formatted message with changes
    """
    if not changes_dict:
        return f"Proyecto {project_id}: Sin cambios"

    change_parts = [f"Proyecto {project_id}: {len(changes_dict)} cambio(s) detectado(s)"]
    for field, diff in sorted(changes_dict.items()):
        old = diff["old"]
        new = diff["new"]
        change_parts.append(f"     • {field}: '{old}' → '{new}'")

    return "\n".join(change_parts)


async def extract_project_card_data(card):
    """Extract project data from card element (supports list/table/grid views)."""
    # List view (Iris list layout)
    row = await card.query_selector(".p-2.row")
    if row:
        # Extract delivery type and status from column 4
        delivery_col = await row.query_selector(":scope > div:nth-child(4)")
        delivery_type, delivery_torres, project_status = (
            await extract_delivery_and_status_from_column(delivery_col)
        )

        # Extract Ley VP from column element (not just text)
        ley_vp_col = await row.query_selector(":scope > div:nth-child(8)")
        has_ley_vp = await extract_ley_vp_from_column(ley_vp_col)

        detail_url_relative = await safe_attr(card, None, "href")

        return {
            "name": await safe_text_in_col(row, 2, ".property-table-title"),
            "zone": await safe_text_in_col(row, 3, ".property-hood"),
            "delivery_type": delivery_type,
            "delivery_torres": delivery_torres,
            "project_status": project_status,
            "price_from": await safe_last_text_in_col(row, 5, ".price.text-secondary.fw-bold"),
            "developer": await safe_text_in_col(row, 6, "p.text-secondary"),
            "commission": await safe_text_in_col(row, 7, ".tag-commision"),
            "has_ley_vp": has_ley_vp,
            "location": await safe_text_in_col(row, 3, ".property-address"),
            "image_url": await safe_attr(card, "img", "src"),
            "detail_url": build_absolute_url(detail_url_relative),
        }

    # Table view (columns by position)
    if await card.query_selector("td"):
        # For table view, try to extract delivery and status similarly
        delivery_td = await card.query_selector("td:nth-child(3)")
        delivery_type, delivery_torres, project_status = (
            await extract_delivery_and_status_from_column(delivery_td)
        )
        if not delivery_type:
            delivery_type = await safe_text(card, "td:nth-child(3)")

        # Extract Ley VP from TD element
        ley_vp_td = await card.query_selector("td:nth-child(7)")
        has_ley_vp = await extract_ley_vp_from_column(ley_vp_td)

        detail_url_relative = await safe_attr(card, "a", "href")

        return {
            "name": await safe_text(card, "td:nth-child(1)"),
            "zone": await safe_text(card, "td:nth-child(2)"),
            "delivery_type": delivery_type,
            "delivery_torres": delivery_torres,
            "project_status": project_status,
            "price_from": await safe_text(card, "td:nth-child(4)"),
            "developer": await safe_text(card, "td:nth-child(5)"),
            "commission": await safe_text(card, "td:nth-child(6)"),
            "has_ley_vp": has_ley_vp,
            "location": None,
            "image_url": await safe_attr(card, "img", "src"),
            "detail_url": build_absolute_url(detail_url_relative),
        }

    # Grid view fallback
    delivery_raw = await safe_text(card, ".property-tags .tag-hand-over")
    delivery_type, delivery_torres, project_status = parse_delivery_info(delivery_raw)
    has_ley_vp = False  # Not available in grid view typically

    return {
        "name": await safe_text(card, ".property-card-title"),
        "zone": None,
        "delivery_type": delivery_type,
        "delivery_torres": delivery_torres,
        "project_status": project_status,
        "price_from": None,
        "developer": None,
        "commission": None,
        "has_ley_vp": has_ley_vp,
        "location": await safe_text(card, ".property-card-location"),
        "image_url": await safe_attr(card, "img", "src"),
        "detail_url": build_absolute_url(await safe_attr(card, "a", "href")),
    }


async def pick_selector(page, selectors, min_count=1):
    """Find first valid selector from list matching min_count threshold."""
    for selector in selectors:
        count = await page.locator(selector).count()
        if count >= min_count:
            return selector, count
    return None, 0


async def scroll_catalog(page, steps=3, distance=1200):
    """Scroll catalog page vertically by specified distance and steps."""
    for _ in range(steps):
        await page.mouse.wheel(0, distance)
        await page.wait_for_timeout(SCROLL_STEP_DELAY_MS)


async def scroll_container_to_bottom(page, container_selector):
    """Scroll container element to bottom, fallback to window scroll."""
    container = page.locator(container_selector).first
    if await container.count():
        try:
            await container.evaluate("el => { el.scrollTop = el.scrollHeight; }")
            await page.wait_for_timeout(SCROLL_AFTER_DELAY_MS)
            return True
        except Exception:
            pass
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(SCROLL_AFTER_DELAY_MS)
    return False


async def scroll_last_row_into_view(page, row_selector):
    """Scroll last matching row element into viewport."""
    last_row = page.locator(row_selector).last
    if await last_row.count():
        try:
            await last_row.scroll_into_view_if_needed(timeout=PAGINATION_VISIBILITY_TIMEOUT_MS)
            await page.wait_for_timeout(SCROLL_AFTER_DELAY_MS)
            return True
        except Exception:
            return False
    return False


async def get_project_hrefs(page, project_selector):
    """Extract all unique href attributes from project selector."""
    return await page.evaluate(
        """
        (sel) => {
            const hrefs = Array.from(document.querySelectorAll(sel))
                .map((el) => el.getAttribute('href'))
                .filter(Boolean);
            return Array.from(new Set(hrefs));
        }
        """,
        project_selector,
    )


async def wait_for_more_projects(page, project_selector, prev_hrefs, row_selector, prev_rows):
    """Wait for new projects to load. Uses polling with evaluate instead of wait_for_function."""
    try:
        # Use polling with evaluate instead of wait_for_function for better reliability
        for attempt in range(POLL_MAX_ATTEMPTS):
            await page.wait_for_timeout(POLL_INTERVAL_MS)

            result = await page.evaluate(
                """
                ({sel, prev, rowSel, prevRows}) => {
                    const hrefs = Array.from(document.querySelectorAll(sel))
                        .map((el) => el.getAttribute('href'))
                        .filter(Boolean);
                    const unique = Array.from(new Set(hrefs));
                    const rows = document.querySelectorAll(rowSel).length;
                    return unique.some((href) => !prev.includes(href)) || rows > prevRows;
                }
                """,
                {
                    "sel": project_selector,
                    "prev": prev_hrefs,
                    "rowSel": row_selector,
                    "prevRows": prev_rows,
                },
            )

            if result:
                return True

        return False
    except Exception:
        return False


async def click_load_more(page, project_selector, row_selector):
    """Click 'Load more' button and wait for new projects to appear."""
    cargar_mas_selector, _ = await pick_selector(page, CARGAR_MAS_SELECTORS, min_count=1)
    if not cargar_mas_selector:
        return False

    cargar_mas_button = page.locator(cargar_mas_selector).first
    try:
        await cargar_mas_button.scroll_into_view_if_needed(timeout=PAGINATION_VISIBILITY_TIMEOUT_MS)
    except Exception:
        pass

    is_visible = await cargar_mas_button.is_visible()
    is_enabled = await cargar_mas_button.is_enabled()
    if not is_visible or not is_enabled:
        return False

    prev_hrefs = await get_project_hrefs(page, project_selector)
    prev_rows = await page.locator(row_selector).count()
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            box = await cargar_mas_button.bounding_box()
            if box:
                await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                await page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            else:
                await cargar_mas_button.click()
        except Exception:
            await cargar_mas_button.click(force=True)

        try:
            await page.wait_for_response(
                lambda r: PROJECTS_API_PATH in r.url and r.status == 200,
                timeout=PAGINATION_LOAD_TIMEOUT_MS,
            )
        except Exception:
            pass

        try:
            await page.wait_for_load_state("networkidle", timeout=PAGINATION_LOAD_TIMEOUT_MS)
        except Exception:
            await page.wait_for_timeout(NETWORKIDLE_FALLBACK_MS)

        await scroll_container_to_bottom(page, CATALOG_SCROLL_CONTAINER)
        await scroll_last_row_into_view(page, row_selector)
        await scroll_catalog(page)

        if await wait_for_more_projects(
            page, project_selector, prev_hrefs, row_selector, prev_rows
        ):
            return True

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(SCROLL_RETRY_DELAY_MS)
        await scroll_last_row_into_view(page, row_selector)
        await scroll_catalog(page, steps=2, distance=1600)
        prev_hrefs = await get_project_hrefs(page, project_selector)
        prev_rows = await page.locator(row_selector).count()

    return False


async def ensure_list_view(page):
    """Switch catalog to list view if toggle button exists."""
    container = page.locator(".container-toggle-list")
    if not await container.count():
        return
    buttons = container.locator("button")
    count = await buttons.count()
    if count == 0:
        return
    # Prefer button with text "Lista"; fallback to second button
    for i in range(count):
        btn = buttons.nth(i)
        text = (await btn.text_content()) or ""
        if "Lista" in text:
            classes = (await btn.get_attribute("class")) or ""
            if "active" in classes:
                return
            await btn.click()
            await page.wait_for_timeout(VIEW_SWITCH_DELAY_MS)
            return
    if count > 1:
        await buttons.nth(1).click()
        await page.wait_for_timeout(VIEW_SWITCH_DELAY_MS)


async def scrape_catalog_phase1():
    """Scrape project catalog with pagination and save artifacts."""
    logger.info("=" * 80)
    logger.info("🤖 Irisbot - Catalog Scraper Phase 1")
    logger.info("=" * 80)
    logger.info("📋 Configuration loaded:")
    logger.info(f"   • Headless mode: {PLAYWRIGHT_HEADLESS}")
    logger.info(f"   • Max iterations: {MAX_PAGES}")
    max_poll_time = POLL_INTERVAL_MS * POLL_MAX_ATTEMPTS
    logger.info(
        f"   • Poll interval: {POLL_INTERVAL_MS}ms × "
        f"{POLL_MAX_ATTEMPTS} attempts = {max_poll_time}ms max"
    )
    logger.info(f"   • Scroll step delay: {SCROLL_STEP_DELAY_MS}ms")
    logger.info(f"   • Scroll after delay: {SCROLL_AFTER_DELAY_MS}ms")
    logger.info(f"   • Network fallback: {NETWORKIDLE_FALLBACK_MS}ms")
    logger.info(f"   • Scroll retry delay: {SCROLL_RETRY_DELAY_MS}ms")
    logger.info(f"   • View switch delay: {VIEW_SWITCH_DELAY_MS}ms")
    logger.info("=" * 80)
    logger.info("")

    conn = setup_db()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
        page = await browser.new_page()
        # Validate catalog URL
        if "example.com" in CATALOG_URL:
            logger.error("CATALOG_URL is a placeholder.")
            logger.error("Set IRIS_CATALOG_URL env var in .env or environment.")
            await browser.close()
            conn.close()
            return

        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        logged_in = await authenticate(page)
        if not logged_in:
            logger.error("Could not authenticate.")
            logger.error("Verify IRIS_EMAIL/IRIS_PASSWORD in .env or environment variables.")
            await browser.close()
            conn.close()
            return

        await page.goto(CATALOG_URL, wait_until="networkidle")

        await ensure_list_view(page)

        if os.environ.get("PW_PAUSE") == "1":
            await page.pause()

        # Wait for content to render before saving artifacts
        try:
            await page.locator("a[href*='/proyecto/']").first.wait_for(
                timeout=PLAYWRIGHT_TIMEOUT_MS
            )
        except Exception:
            pass

        # Screenshot 1: Initial catalog state
        await page.screenshot(path=str(OUTPUT_DIR / "01_catalog_initial.png"), full_page=True)
        html = await page.content()
        (OUTPUT_DIR / "01_catalog_initial.html").write_text(html, encoding="utf-8")

        project_selector, project_count = await pick_selector(
            page, PROJECT_CARD_SELECTORS, min_count=1
        )
        if not project_selector:
            logger.error("No se encontró selector de tarjeta de proyecto.")
            await browser.close()
            conn.close()
            return
        logger.info(f"Project selector used: {project_selector} (count={project_count})")
        if project_count > 0:
            first_elem = page.locator(project_selector).first
            try:
                (OUTPUT_DIR / "catalog_row_sample.html").write_text(
                    await first_elem.evaluate("el => el.outerHTML"),
                    encoding="utf-8",
                )
            except Exception:
                pass
        projects = []
        seen_detail_urls = set()
        new_projects = []  # Track newly added projects
        new_project_ids = []  # Track IDs of newly added projects
        updated_projects = []  # Track updated projects with their changes
        updated_project_ids = []  # Track IDs of updated projects
        unchanged_project_ids = []  # Track IDs of unchanged projects
        page_iteration = 0
        start_time = time.time()

        logger.info("=" * 80)
        logger.info("🚀 Starting catalog pagination and data extraction")
        logger.info(f"Maximum iterations configured: {MAX_PAGES}")
        logger.info("=" * 80)

        while page_iteration < MAX_PAGES:
            page_iteration += 1
            iteration_start = time.time()

            # Local counters for this iteration (reset each iteration)
            new_this_iteration = 0
            updated_this_iteration = 0
            unchanged_this_iteration = 0

            logger.info("")
            logger.info("=" * 80)
            logger.info(f"📄 ITERATION {page_iteration}/{MAX_PAGES}")
            logger.info("=" * 80)

            cards_before = await page.query_selector_all(project_selector)
            visible_before = len(cards_before)
            row_count_before = await page.locator(COLUMN_ROW_SELECTOR).count()
            hrefs_before = await get_project_hrefs(page, project_selector)
            logger.debug(f"Elements found: {visible_before} (rows: {row_count_before})")
            logger.debug(f"Unique hrefs: {len(hrefs_before)}")

            new_projects_count = 0
            for card in cards_before:
                data = await extract_project_card_data(card)
                if data.get("detail_url") in seen_detail_urls:
                    continue
                if data.get("detail_url"):
                    seen_detail_urls.add(data["detail_url"])
                if not data.get("name"):
                    continue
                projects.append(data)
                new_projects_count += 1
                # Log individual projects only at DEBUG level
                proyecto_info = (
                    f"{data['name']} | {data.get('zone')} | "
                    f"{data.get('delivery_type')} [{data.get('project_status') or 'N/A'}]"
                )
                precio_info = (
                    f"{data.get('price_from')} | {data.get('developer')} | "
                    f"{data.get('commission')} | VP: {data.get('has_ley_vp')}"
                )
                logger.debug(f"Proyecto: {proyecto_info}")
                logger.debug(f"Info: {precio_info}")

                # Extract project_id from detail_url
                project_id = extract_project_id_from_url(data.get("detail_url"))
                if not project_id:
                    logger.warning(
                        f"Could not extract project_id from URL: {data.get('detail_url')}"
                    )
                    continue

                # Check if project already exists in database and get full row
                c = conn.cursor()
                c.execute(
                    """SELECT project_id, detail_url, name, zone, delivery_type, delivery_torres,
                             project_status, price_from, developer, commission,
                             has_ley_vp, location, image_url, scraped_at, updated_at
                        FROM projects WHERE project_id = ?""",
                    (project_id,),
                )
                existing_row = c.fetchone()
                is_new_project = existing_row is None

                # Detect if existing project has changed
                has_changes = False
                changes_dict = {}
                if existing_row:
                    has_changes, changes_dict = compare_project_data(existing_row, data)

                # Only update if project is new or has changes
                if is_new_project or has_changes:
                    conn.execute(
                        """
                        INSERT INTO projects (
                            project_id, detail_url, name, zone, delivery_type, delivery_torres,
                            project_status, price_from, developer, commission,
                            has_ley_vp, location, image_url, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(project_id) DO UPDATE SET
                            detail_url = excluded.detail_url,
                            name = excluded.name,
                            zone = excluded.zone,
                            delivery_type = excluded.delivery_type,
                            delivery_torres = excluded.delivery_torres,
                            project_status = excluded.project_status,
                            price_from = excluded.price_from,
                            developer = excluded.developer,
                            commission = excluded.commission,
                            has_ley_vp = excluded.has_ley_vp,
                            location = excluded.location,
                            image_url = excluded.image_url,
                            updated_at = CURRENT_TIMESTAMP
                    """,
                        (
                            project_id,
                            data.get("detail_url"),
                            data["name"],
                            data.get("zone"),
                            data.get("delivery_type"),
                            data.get("delivery_torres"),
                            data.get("project_status"),
                            data.get("price_from"),
                            data.get("developer"),
                            data.get("commission"),
                            data.get("has_ley_vp"),
                            data.get("location"),
                            data.get("image_url"),
                        ),
                    )
                    conn.commit()

                    # Log change details only at INFO level
                    if is_new_project:
                        logger.info(f"✨ NEW PROJECT: ID {project_id} - {data['name']}")
                        new_projects.append(data)
                        new_project_ids.append(project_id)
                        new_this_iteration += 1
                    else:
                        logger.info(format_change_message(project_id, changes_dict))
                        updated_projects.append({"id": project_id, "changes": changes_dict})
                        updated_project_ids.append(project_id)
                        updated_this_iteration += 1
                else:
                    # Project exists and hasn't changed
                    unchanged_project_ids.append(project_id)
                    unchanged_this_iteration += 1

            iteration_elapsed = time.time() - iteration_start

            logger.info("")
            logger.info("─" * 80)
            logger.info(f"✅ Iteration {page_iteration} completed")
            logger.info(f"   • New projects: {new_this_iteration}")
            logger.info(f"   • Updated projects: {updated_this_iteration}")
            logger.info(f"   • Unchanged projects: {unchanged_this_iteration}")
            logger.info(f"   • Total projects accumulated: {len(projects)}")
            logger.info(f"   • Iteration duration: {iteration_elapsed:.2f}s")
            logger.info("─" * 80)

            screenshot_num = str(page_iteration + 1).zfill(2)
            await page.screenshot(
                path=str(OUTPUT_DIR / f"{screenshot_num}_catalog_page_{page_iteration-1}.png"),
                full_page=True,
            )
            html = await page.content()
            (OUTPUT_DIR / f"{screenshot_num}_catalog_page_{page_iteration-1}.html").write_text(
                html, encoding="utf-8"
            )
            logger.debug(f"Screenshot saved: {screenshot_num}_catalog_page_{page_iteration-1}.png")

            logger.debug("Searching for 'Load more' button...")
            loaded_more = await click_load_more(page, project_selector, COLUMN_ROW_SELECTOR)
            if not loaded_more:
                logger.info("No more elements loaded. End of catalog reached.")
                break

        if os.environ.get("WAIT_FOR_APPROVAL") == "1":
            input("Review the screen and press ENTER to finish...")

        await browser.close()
    conn.close()

    total_elapsed = time.time() - start_time
    avg_iteration_time = total_elapsed / page_iteration if page_iteration > 0 else 0

    logger.info("")
    logger.info("=" * 100)
    logger.info("🎉 CATALOG SCRAPING COMPLETED SUCCESSFULLY")
    logger.info("=" * 100)
    logger.info("")
    logger.info("📊 EXECUTION SUMMARY:")
    logger.info(f"   • Total projects captured: {len(projects)}")
    logger.info(f"   • Total unique URLs: {len(seen_detail_urls)}")
    logger.info("")
    logger.info("📈 DATABASE CHANGES:")
    logger.info(f"   • New projects added: {len(new_project_ids)}")
    if new_project_ids:
        new_ids_str = ", ".join(map(str, new_project_ids[:10]))
        if len(new_project_ids) > 10:
            new_ids_str += f", ... ({len(new_project_ids) - 10} more)"
        logger.info(f"     Project IDs: {new_ids_str}")
    logger.info(f"   • Projects updated (with changes detected): {len(updated_project_ids)}")
    if updated_project_ids:
        updated_ids_str = ", ".join(map(str, updated_project_ids[:10]))
        if len(updated_project_ids) > 10:
            updated_ids_str += f", ... ({len(updated_project_ids) - 10} more)"
        logger.info(f"     Project IDs: {updated_ids_str}")
    logger.info(f"   • Projects without changes (NO update applied): {len(unchanged_project_ids)}")
    logger.info("")
    logger.info("⏱️  PERFORMANCE METRICS:")
    logger.info(f"   • Total iterations performed: {page_iteration}")
    logger.info(f"   • Total execution time: {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
    logger.info(f"   • Average time per iteration: {avg_iteration_time:.2f}s")
    if page_iteration > 0:
        logger.info(f"   • Average projects per iteration: {len(projects)/page_iteration:.1f}")
    logger.info("")
    logger.info("📁 OUTPUT FILES:")
    logger.info(f"   • Database: {DB_PATH}")
    logger.info(f"   • Screenshots & HTML: {OUTPUT_DIR}/")
    logger.info("      - 01_catalog_initial.png / .html (Initial state)")
    for i in range(page_iteration):
        screenshot_num = str(i + 2).zfill(2)
        logger.info(f"      - {screenshot_num}_catalog_page_{i}.png / .html (Iteration {i+1})")
    logger.info("")
    logger.info("=" * 100)


if __name__ == "__main__":
    asyncio.run(scrape_catalog_phase1())
