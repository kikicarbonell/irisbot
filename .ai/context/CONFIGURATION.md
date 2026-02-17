# Configuration Guide

This document describes all configuration options available in the Irisbot scraper. Configuration is managed through environment variables that can be set in a `.env` file at the project root or directly in your system environment.

---

## 📋 Table of Contents

- [Authentication](#authentication)
- [Project Settings](#project-settings)
- [Database Configuration](#database-configuration)
- [Browser Settings](#browser-settings)
- [Pagination & Timeouts](#pagination--timeouts)
- [Scraper Wait Times](#scraper-wait-times)
- [Networking & Downloads](#networking--downloads)
- [Retry & Limits](#retry--limits)
- [Iris Platform URLs](#iris-platform-urls)
- [Logging](#logging)

---

## Authentication

### `IRIS_EMAIL`
- **Type:** String (required)
- **Default:** None
- **Description:** Email address for authenticating with the Iris platform
- **Example:** `IRIS_EMAIL=your_email@example.com`

### `IRIS_PASSWORD`
- **Type:** String (required)
- **Default:** None
- **Description:** Password for authenticating with the Iris platform
- **Example:** `IRIS_PASSWORD=your_secure_password`

⚠️ **Security Note:** Never commit credentials to version control. Always use a `.env` file (which is in `.gitignore`) or environment variables.

---

## Project Settings

### `PROJECT_NAME`
- **Type:** String
- **Default:** `"irisbot"`
- **Description:** Project identifier used for directory naming
- **Example:** `PROJECT_NAME=irisbot`

### `BASE_DIR`
- **Type:** Path
- **Default:** Current working directory
- **Description:** Base directory for project files and artifacts
- **Example:** `BASE_DIR=/path/to/project`

---

## Database Configuration

### `DB_FILENAME`
- **Type:** String
- **Default:** `"irisbot.db"`
- **Description:** SQLite database filename
- **Example:** `DB_FILENAME=catalog_projects.db`

### `DB_DSN`
- **Type:** String
- **Default:** `"sqlite:///{BASE_DIR}/{DB_FILENAME}"`
- **Description:** SQLAlchemy/SQLModel database connection string
- **Example:** `DB_DSN=sqlite:///catalog_projects.db`

---

## Browser Settings

### `PLAYWRIGHT_HEADLESS`
- **Type:** Boolean
- **Default:** `True`
- **Description:** Run browser in headless mode (no GUI)
- **Values:** `1` / `true` / `True` (headless), `0` / `false` / `False` (with GUI)
- **Example:** `PLAYWRIGHT_HEADLESS=False`

### `PLAYWRIGHT_TIMEOUT_MS`
- **Type:** Integer (milliseconds)
- **Default:** `30000` (30 seconds)
- **Description:** General timeout for browser operations
- **Example:** `PLAYWRIGHT_TIMEOUT_MS=45000`

---

## Authentication Timeouts

**Purpose:** Separate timeouts for login/authentication process which requires more time for redirects and server processing. These are independent from scraping/pagination timeouts.

### `AUTH_BUTTON_CLICK_DELAY_MS`
- **Type:** Integer (milliseconds)
- **Default:** `2000` (1 seconds)
- **Description:** Wait time after clicking the login button, before checking for redirect
- **Use case:** Allows form submission and server-side authentication to process
- **Example:** `AUTH_BUTTON_CLICK_DELAY_MS=3000`

### `AUTH_REDIRECT_TIMEOUT_MS`
- **Type:** Integer (milliseconds)
- **Default:** `45000` (45 seconds)
- **Description:** Maximum time to wait for URL redirect after login
- **Use case:** Waiting for authentication server response and redirect to projects page
- **Example:** `AUTH_REDIRECT_TIMEOUT_MS=60000`

### `AUTH_NETWORKIDLE_TIMEOUT_MS`
- **Type:** Integer (milliseconds)
- **Default:** `45000` (45 seconds)
- **Description:** Maximum time to wait for page load after login redirect
- **Use case:** Waiting for projects page to fully load after successful authentication
- **Example:** `AUTH_NETWORKIDLE_TIMEOUT_MS=60000`

---

## Pagination & Timeouts

### `PAGINATION_LOAD_TIMEOUT_MS`
- **Type:** Integer (milliseconds)
- **Default:** `10000` (10 seconds)
- **Description:** Maximum time to wait for page content to load after pagination
- **Use case:** Waiting for API response after clicking "Load more"
- **Example:** `PAGINATION_LOAD_TIMEOUT_MS=15000`

### `PAGINATION_VISIBILITY_TIMEOUT_MS`
- **Type:** Integer (milliseconds)
- **Default:** `3000` (3 seconds)
- **Description:** Maximum time to wait for pagination button to become visible
- **Use case:** Finding the "Cargar más" button
- **Example:** `PAGINATION_VISIBILITY_TIMEOUT_MS=5000`

---

## Scraper Wait Times

These settings control the timing behavior of the scraper. The default values are **optimized for performance** while maintaining reliability. Increase values if you experience timeout errors or content loading issues.

### `POLL_INTERVAL_MS`
- **Type:** Integer (milliseconds)
- **Default:** `200` (0.2 seconds)
- **Description:** Wait time between polling attempts when checking for new content
- **Performance impact:** Lower = faster detection, higher CPU usage; too low may cause issues
- **Example:** `POLL_INTERVAL_MS=300`
- **Recommended range:** 100-400ms

### `POLL_MAX_ATTEMPTS`
- **Type:** Integer
- **Default:** `15` (total 3 seconds @ 200ms interval)
- **Description:** Maximum number of polling attempts before giving up
- **Performance impact:** Higher = more reliable but slower
- **Example:** `POLL_MAX_ATTEMPTS=20`
- **Recommended range:** 10-25 attempts

### `SCROLL_STEP_DELAY_MS`
- **Type:** Integer (milliseconds)
- **Default:** `200` (0.2 seconds)
- **Description:** Delay between each scroll step when scrolling through catalog
- **Performance impact:** Lower = faster scrolling, may miss dynamic content
- **Example:** `SCROLL_STEP_DELAY_MS=250`
- **Recommended range:** 150-400ms

### `SCROLL_AFTER_DELAY_MS`
- **Type:** Integer (milliseconds)
- **Default:** `300` (0.3 seconds)
- **Description:** Delay after completing a scroll operation
- **Performance impact:** Allows time for dynamic content to render
- **Example:** `SCROLL_AFTER_DELAY_MS=400`
- **Recommended range:** 200-500ms

### `NETWORKIDLE_FALLBACK_MS`
- **Type:** Integer (milliseconds)
- **Default:** `800` (0.8 seconds)
- **Description:** Fallback delay when network idle detection fails
- **Performance impact:** Safety net for slow network responses; critical for login stability
- **Example:** `NETWORKIDLE_FALLBACK_MS=1000`
- **Recommended range:** 500-2000ms

### `SCROLL_RETRY_DELAY_MS`
- **Type:** Integer (milliseconds)
- **Default:** `500` (0.5 seconds)
- **Description:** Delay before retrying scroll operations after initial failure
- **Performance impact:** Gives page more time to stabilize
- **Example:** `SCROLL_RETRY_DELAY_MS=700`
- **Recommended range:** 300-1000ms

### `VIEW_SWITCH_DELAY_MS`
- **Type:** Integer (milliseconds)
- **Default:** `200` (0.2 seconds)
- **Description:** Delay after switching view modes (list/grid)
- **Performance impact:** Allows UI to update after view change
- **Example:** `VIEW_SWITCH_DELAY_MS=300`
- **Recommended range:** 150-400ms

---

## Networking & Downloads

### `CONCURRENT_DOWNLOADS`
- **Type:** Integer
- **Default:** `5`
- **Description:** Maximum number of simultaneous file downloads
- **Example:** `CONCURRENT_DOWNLOADS=10`

### `DOWNLOAD_TIMEOUT_S`
- **Type:** Integer (seconds)
- **Default:** `60`
- **Description:** Maximum time to wait for a single file download
- **Example:** `DOWNLOAD_TIMEOUT_S=120`

### `USER_AGENT`
- **Type:** String
- **Default:** `"irisbot/1.0 (+https://example.com)"`
- **Description:** User agent string for HTTP requests
- **Example:** `USER_AGENT="MyBot/2.0 (+https://mysite.com)"`

---

## Retry & Limits

### `REQUEST_RETRY_COUNT`
- **Type:** Integer
- **Default:** `3`
- **Description:** Number of retry attempts for failed requests
- **Example:** `REQUEST_RETRY_COUNT=5`

### `REQUEST_RETRY_BACKOFF_S`
- **Type:** Float (seconds)
- **Default:** `1.5`
- **Description:** Multiplier for exponential backoff between retries
- **Example:** `REQUEST_RETRY_BACKOFF_S=2.0`

### `CATALOG_MAX_PAGES`
- **Type:** Integer
- **Default:** `200`
- **Description:** Maximum number of pagination iterations in catalog scraper
- **Example:** `CATALOG_MAX_PAGES=50`

---

## Iris Platform URLs

### `IRIS_BASE_URL`
- **Type:** String (URL)
- **Default:** `"https://iris.infocasas.com.uy"`
- **Description:** Base URL for the Iris platform
- **Example:** `IRIS_BASE_URL=https://iris.infocasas.com.uy`

### `IRIS_LOGIN_URL`
- **Type:** String (URL)
- **Default:** `"{IRIS_BASE_URL}/iniciar-sesion"`
- **Description:** Login page URL (automatically derived from base URL)
- **Example:** `IRIS_LOGIN_URL=https://iris.infocasas.com.uy/iniciar-sesion`

### `IRIS_CATALOG_URL`
- **Type:** String (URL)
- **Default:** `"{IRIS_BASE_URL}/proyectos?country=1&order=promos%2Cpopularity"`
- **Description:** Catalog page URL with default filters
- **Example:** `IRIS_CATALOG_URL=https://iris.infocasas.com.uy/proyectos?country=1`

---

## Logging

### `LOG_LEVEL`
- **Type:** String
- **Default:** `"INFO"`
- **Description:** Logging verbosity level. Controls how much detail is shown during execution.
- **Values:**
  - `INFO` (recommended): Shows iteration summaries and important events only
  - `DEBUG`: Shows detailed information including each project captured, elements found, screenshots saved, etc.
  - `WARNING`: Shows only warnings and errors
  - `ERROR`: Shows only errors
  - `CRITICAL`: Shows only critical errors
- **Example:** `LOG_LEVEL=DEBUG`

**INFO level output (clean):**
```
📄 ITERATION 1/200
================================================================================

────────────────────────────────────────────────────────────────────────────────
✅ Iteration 1 completed
   • New projects this iteration: 25
   • Total projects accumulated: 25
   • Iteration duration: 2.15s
────────────────────────────────────────────────────────────────────────────────
```

**DEBUG level output (verbose):**
- Includes all INFO messages, plus:
- Elements found in each iteration
- Each project captured with details (name, zone, price, developer, etc.)
- Screenshot and HTML file saves
- Button searches and scroll operations

---

## 📝 Example `.env` File

Here's a complete example of a `.env` file with common customizations:

```bash
# Required: Authentication
IRIS_EMAIL=your_email@example.com
IRIS_PASSWORD=your_secure_password

# Browser
PLAYWRIGHT_HEADLESS=True
PLAYWRIGHT_TIMEOUT_MS=30000

# Performance tuning (balanced defaults, reliable ~2-3s/iteration)
POLL_INTERVAL_MS=200
POLL_MAX_ATTEMPTS=15
SCROLL_STEP_DELAY_MS=200
SCROLL_AFTER_DELAY_MS=300
NETWORKIDLE_FALLBACK_MS=800

# Catalog scraping
CATALOG_MAX_PAGES=200

# Logging
LOG_LEVEL=INFO
```

---

## 🎯 Performance Tuning Guide

### Default Configuration (Balanced - Reliable Speed ~2-3s per iteration)
The default values balance speed with reliability:
```bash
POLL_INTERVAL_MS=200          # 3s total polling time
POLL_MAX_ATTEMPTS=15
SCROLL_STEP_DELAY_MS=200
SCROLL_AFTER_DELAY_MS=300
NETWORKIDLE_FALLBACK_MS=800
SCROLL_RETRY_DELAY_MS=500
VIEW_SWITCH_DELAY_MS=200
```

### For Faster Scraping (May cause login/timeout issues)
```bash
POLL_INTERVAL_MS=100
POLL_MAX_ATTEMPTS=10          # 1s total polling time
SCROLL_STEP_DELAY_MS=150
SCROLL_AFTER_DELAY_MS=200
NETWORKIDLE_FALLBACK_MS=500
SCROLL_RETRY_DELAY_MS=300
VIEW_SWITCH_DELAY_MS=150
```

### For Maximum Reliability (Slower but very stable)
```bash
POLL_INTERVAL_MS=300
POLL_MAX_ATTEMPTS=20          # 6s total polling time
SCROLL_STEP_DELAY_MS=400
SCROLL_AFTER_DELAY_MS=500
NETWORKIDLE_FALLBACK_MS=1500
SCROLL_RETRY_DELAY_MS=800
VIEW_SWITCH_DELAY_MS=300
```

### For Debugging (Visible Browser)
```bash
PLAYWRIGHT_HEADLESS=False
LOG_LEVEL=DEBUG
CATALOG_MAX_PAGES=3
```

---

## 🔧 Troubleshooting

### "Timeout waiting for projects to load"
- Increase: `PAGINATION_LOAD_TIMEOUT_MS`, `POLL_MAX_ATTEMPTS`
- Or decrease: `POLL_INTERVAL_MS` (for faster detection)

### "Content not detected after scrolling"
- Increase: `SCROLL_AFTER_DELAY_MS`, `SCROLL_STEP_DELAY_MS`

### "Network idle timeout"
- Increase: `NETWORKIDLE_FALLBACK_MS`, `PLAYWRIGHT_TIMEOUT_MS`

### "Scraper running too slow"
- Decrease: `POLL_INTERVAL_MS`, `SCROLL_STEP_DELAY_MS`, `SCROLL_AFTER_DELAY_MS`
- Note: May reduce reliability on slow connections

---

## 📚 Related Documentation

- [Project Overview](.ai/context/PROJECT_OVERVIEW.md)
- [Architecture](.ai/context/ARCHITECTURE.md)
- [Testing Guide](.ai/guidelines/TESTING_GUIDE.md)
- [README](../../README.md)
