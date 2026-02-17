# ARCHITECTURE - Irisbot Technical Design

## 🏗️ Arquitectura General del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                     IRISBOT SCRAPER SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRY POINT LAYER                            │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  scrape_catalog_phase1.py                                 │ │
│  │  - Main orchestrator for Phase 1                          │ │
│  │  - Handles pagination loop                                │ │
│  │  - Extracts project data                                  │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     CORE MODULES LAYER                          │
│  ┌───────────────┬───────────────┬──────────────────────────┐  │
│  │  auth.py      │  config.py    │  iris_selectors.py       │  │
│  │               │               │                          │  │
│  │  - Login      │  - .env vars  │  - CSS selectors        │  │
│  │  - Session    │  - URLs       │  - XPath expressions    │  │
│  │               │  - Timeouts   │                          │  │
│  └───────────────┴───────────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER AUTOMATION LAYER                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Playwright (async API)                       │ │
│  │  - Browser: Chromium (headless/headful)                  │ │
│  │  - Page management                                        │ │
│  │  - Network interception                                   │ │
│  │  - JavaScript execution in browser context               │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                       │
│  ┌───────────────┬───────────────┬──────────────────────────┐  │
│  │  database.py  │  db_manager.py│  catalog_projects.db     │  │
│  │               │               │                          │  │
│  │  - Schema     │  - CRUD ops   │  - SQLite storage       │  │
│  │  - Migrations │  - Queries    │  - 129 projects         │  │
│  └───────────────┴───────────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     UTILITIES LAYER                             │
│  ┌───────────────┬───────────────┬──────────────────────────┐  │
│  │  utils.py     │downloader.py  │  OUTPUT ARTIFACTS        │  │
│  │               │               │                          │  │
│  │  - Helpers    │  - File DL    │  - Screenshots           │  │
│  │  - Parsing    │  - Asset mgmt │  - HTML snapshots        │  │
│  └───────────────┴───────────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Estructura de Módulos

### **1. scrape_catalog_phase1.py** (Entry Point)
**Responsabilidad:** Orquestador principal del scraping de catálogo

**Funciones clave:**
```python
async def scrape_catalog_phase1():
    """Main orchestrator for catalog scraping"""
    # 1. Setup database
    # 2. Launch browser
    # 3. Authenticate
    # 4. Load catalog page
    # 5. Pagination loop (click "Cargar más")
    # 6. Extract projects per iteration
    # 7. Save to database

async def click_load_more(page, project_selector, row_selector):
    """Clicks 'Cargar más' button and waits for new content"""
    # - Find button
    # - Scroll into view
    # - Click
    # - Wait for new projects to load

async def wait_for_more_projects(page, project_selector, prev_hrefs, ...):
    """Polls DOM until new projects appear"""
    # - Poll every 500ms (20 attempts = 10s total)
    # - Check for new hrefs OR increased row count
    # - Return True if detected, False if timeout

async def extract_project_card_data(card):
    """Extracts all fields from a project card"""
    # Returns: {name, zone, delivery_type, price_from, ...}
```

**Flujo de ejecución:**
1. Conecta a DB (SQLite)
2. Lanza Playwright → Chromium headless
3. Navega a `/iniciar-sesion`
4. Autentica con `authenticate(page)`
5. Navega a catálogo `/proyectos?...`
6. Loop mientras exista botón "Cargar más":
   - Extrae proyectos visibles
   - Guarda en DB (INSERT OR IGNORE)
   - Click botón
   - Espera nuevos proyectos
7. Cierra navegador y DB

---

### **2. auth.py** (Authentication)
**Responsabilidad:** Manejo de login en Iris

**Función principal:**
```python
async def authenticate(page: Page, email=None, password=None) -> bool:
    """
    Authenticates user in Iris portal

    Process:
    1. Wait for email input
    2. Fill email and password
    3. Click submit button
    4. Wait for redirect to /feed or /proyectos
    5. Return True if successful
    """
```

**Selectores utilizados:**
- `LOGIN_EMAIL_INPUT` - Input de email
- `LOGIN_PASSWORD_INPUT` - Input de contraseña
- `LOGIN_SUBMIT_BUTTON` - Botón de envío

**Manejo de errores:**
- Timeout si selectores no aparecen (30s)
- Validación de credenciales incorrectas
- Verificación de redirección exitosa

---

### **3. config.py** (Configuration)
**Responsabilidad:** Carga de configuración desde variables de entorno

**Variables cargadas:**
```python
# Authentication
IRIS_EMAIL: str
IRIS_PASSWORD: str

# URLs
IRIS_BASE_URL: str = "https://iris.infocasas.com.uy"
IRIS_LOGIN_URL: str = f"{IRIS_BASE_URL}/iniciar-sesion"
IRIS_CATALOG_URL: str = f"{IRIS_BASE_URL}/proyectos?country=1&order=promos%2Cpopularity"

# Playwright settings
PLAYWRIGHT_HEADLESS: bool = True
PLAYWRIGHT_TIMEOUT_MS: int = 30000

# Pagination settings
PAGINATION_LOAD_TIMEOUT_MS: int = 10000
PAGINATION_VISIBILITY_TIMEOUT_MS: int = 3000

# Logging
LOG_LEVEL: str = "INFO"
```

**Validación:**
- Verifica que `.env` existe
- Valida credenciales no vacías
- Proporciona valores por defecto seguros

---

### **4. iris_selectors.py** (CSS Selectors)
**Responsabilidad:** Centralización de selectores CSS/XPath

**Selectores definidos:**
```python
# Authentication
LOGIN_EMAIL_INPUT = "input[type='email'], input[name*='email' i]"
LOGIN_PASSWORD_INPUT = "input[type='password']"
LOGIN_SUBMIT_BUTTON = "button[type='submit']"

# Project cards (Catalog - PHASE 1)
PROJECT_CARD_CONTAINER = "div.gx-2.gy-3.mb-4.mt-1.mt-lg-0.row"
PROJECT_CARD_LINK = "a[href*='/proyecto/']"

# Pagination
LOAD_MORE_BUTTON = "button:has-text('Cargar más')"

# Project detail page (PHASE 2 - future)
PROJECT_TITLE = "h1.project-title"
PROJECT_DESCRIPTION = "div.project-description"
UNITS_TABLE = "table.units-table"
DEVELOPER_INFO_BUTTON = "button:has-text('Más información')"
```

**Rationale:**
- Permite cambiar selectores en un solo lugar
- Facilita mantenimiento si Iris actualiza su UI
- Documentación centralizada de estructura del DOM

---

### **5. database.py** (DB Schema)
**Responsabilidad:** Definición del esquema de base de datos

**Esquema actual (Fase 1):**
```sql
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    detail_url TEXT UNIQUE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Índices:**
- `detail_url` - UNIQUE constraint para evitar duplicados
- `PRIMARY KEY` en `id`

**Migraciones:**
- Función `setup_db()` con manejo de schema legacy
- Renombra tablas antiguas a `_old` si detecta cambios

---

### **6. db_manager.py** (Database Operations)
**Responsabilidad:** Operaciones CRUD sobre la base de datos

**Funciones:**
```python
def get_connection() -> sqlite3.Connection:
    """Returns DB connection"""

def insert_project(conn, project_data: dict):
    """Inserts or ignores project"""

def get_all_projects(conn) -> list[dict]:
    """Returns all projects"""

def get_project_by_url(conn, url: str) -> dict:
    """Finds project by detail_url"""
```

---

### **7. utils.py** (Utilities)
**Responsabilidad:** Funciones auxiliares reutilizables

**Funciones:**
```python
def safe_filename(text: str) -> str:
    """Sanitizes filename for filesystem"""

def parse_price(price_text: str) -> float:
    """Parses 'USD 120.000' → 120000.0"""

async def take_screenshot(page, path: str):
    """Captures page screenshot"""
```

---

### **8. downloader.py** (Asset Management)
**Responsabilidad:** Descarga de archivos (PDFs, imágenes)

**Funciones:**
```python
async def download_file(page, url: str, dest_path: str):
    """Downloads file from URL"""

async def download_pdf(page, pdf_url: str, project_id: int):
    """Downloads project PDF brochure"""
```

---

## 🔄 Flujo de Datos (Phase 1)

```
┌─────────────────────────────────────────────────────────────┐
│  1. START: scrape_catalog_phase1.py                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  2. SETUP: database.py → setup_db()                         │
│     Creates catalog_projects.db                             │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  3. BROWSER: Playwright launch                              │
│     chromium.launch(headless=PLAYWRIGHT_HEADLESS)           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  4. AUTH: auth.py → authenticate(page)                      │
│     POST /iniciar-sesion → redirect to /feed               │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  5. CATALOG: Navigate to /proyectos                         │
│     Wait for network idle                                   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  6. PAGINATION LOOP (iterations: 11)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ A. Extract visible projects (12 per iteration)         ││
│  │    - query_selector_all(PROJECT_CARD_LINK)             ││
│  │    - extract_project_card_data(card)                   ││
│  │                                                         ││
│  │ B. Save to DB                                          ││
│  │    - INSERT OR IGNORE INTO projects                    ││
│  │                                                         ││
│  │ C. Click "Cargar más"                                  ││
│  │    - click_load_more(page, selector, row_selector)     ││
│  │    - wait_for_more_projects() → poll 20x500ms          ││
│  │                                                         ││
│  │ D. Check if more projects loaded                       ││
│  │    - Compare hrefs before/after                        ││
│  │    - If no new → break loop                            ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Result: 129 unique projects captured                       │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  7. CLEANUP: Close browser, commit DB                       │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  8. SUCCESS: catalog_projects.db with 129 projects          │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Decisiones de Diseño Clave

### **1. Por qué Playwright vs Selenium/Requests**
- ✅ **Mejor manejo de SPAs** (React/Vue con contenido dinámico)
- ✅ **Async/await nativo** (mejor performance)
- ✅ **Network interception** built-in
- ✅ **Headless mode** más estable que Selenium
- ✅ **Auto-wait** para elementos (menos flaky tests)

### **2. Por qué SQLite vs PostgreSQL/MySQL**
- ✅ **Sin servidor** (más simple para desarrollo)
- ✅ **Portable** (archivo único)
- ✅ **Suficiente para ~100k registros** estimados
- ✅ **Puede migrar a PostgreSQL** en Fase 3 si necesario

### **3. Por qué Polling vs wait_for_function**
**Problema:** `page.wait_for_function()` tiene timeout fijo de 10s y falla si no detecta cambio inmediato.

**Solución:** Polling manual con `page.evaluate()`:
```python
for attempt in range(20):  # 20 * 500ms = 10s
    await page.wait_for_timeout(500)
    result = await page.evaluate("...")
    if result:
        return True
```

**Beneficios:**
- ✅ Más robusto ante latencia de red
- ✅ Permite logging intermedio
- ✅ Control granular de timeouts

### **4. Por qué `a[href*='/proyecto/']` vs `.table-row`**
**Problema inicial:** Se intentó usar `.table-row` como selector, pero NO existe en el DOM.

**Descubrimiento:** Los proyectos son `<a>` tags con `href="/proyecto/XXX"`.

**Lección aprendida:** Siempre inspeccionar DOM real, no asumir estructura.

---

## 🧪 Testing Strategy

### Unit Tests (`tests/`)
- ✅ `test_config.py` - Config loading
- ✅ `test_database.py` - DB operations
- ✅ `test_auth.py` - Authentication logic
- ✅ `test_utils.py` - Helper functions

### Integration Tests
- ✅ `test_scraper_flow.py` - End-to-end scraping
- ⏳ `test_pagination.py` - Pagination edge cases (pending)

### CI/CD Pipeline
```yaml
# .github/workflows/ci.yml
- pytest tests/
- codecov report
- lint with flake8
```

---

## 📊 Performance Metrics

### Scraping Performance (Phase 1)
- **Total time:** ~3-4 minutes para 129 proyectos
- **Throughput:** ~30-40 proyectos/minuto
- **Network:** ~500 KB de HTML transferido
- **Pagination iterations:** 11
- **Success rate:** 100%

### Resource Usage
- **Memory:** ~150-200 MB (Playwright + Chromium)
- **CPU:** Moderado (async I/O bound)
- **Disk:** ~50 MB (DB + screenshots)

---

## 🔮 Future Architecture (Phase 2+)

### Planned Enhancements

**1. Multi-table Schema**
```sql
-- projects (existing)
-- units (new)
CREATE TABLE units (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    unit_number TEXT,
    typology TEXT,
    price_cash REAL,
    price_installments REAL,
    price_list REAL,
    sqm_internal REAL,
    has_rent BOOLEAN,
    has_360_view BOOLEAN
);

-- developer_assets (new)
CREATE TABLE developer_assets (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    asset_type TEXT,  -- 'brochure', 'memoria', 'logo'
    file_url TEXT,
    local_path TEXT
);
```

**2. Concurrent Scraping**
- Use `asyncio.Semaphore` to limit concurrent requests
- Parallel scraping of project detail pages
- Rate limiting to avoid IP blocks

**3. Incremental Updates**
- Track `last_scraped_at` timestamp
- Re-scrape only updated projects
- Diff detection (price changes, new units)

---

**Última actualización:** Febrero 16, 2026
