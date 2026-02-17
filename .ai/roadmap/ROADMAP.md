# ROADMAP - Irisbot Development Plan

## 🎯 Project Vision

Build a comprehensive, automated scraper for the Iris PropertyTech platform that extracts complete real estate inventory data (projects, units, assets) for analysis, reporting, and integration with third-party systems.

---

## 📊 Development Phases

```
Timeline: 3-4 weeks total

Week 1: Phase 1 - Catalog Scraping ✅ COMPLETE
Week 2: Phase 2 - Detail Scraping 🚧 IN PROGRESS
Week 3: Phase 3 - Export & API 🔮 PLANNED
Week 4: Phase 4 - Production & Automation 🔮 PLANNED
```

---

## ✅ Phase 1: Catalog Inventory Scraping

**Status:** ✅ **COMPLETE** (Feb 14, 2026)

### Objectives
Extract complete catalog of property development projects from Iris.

### Deliverables
- [x] Authentication module (`auth.py`)
- [x] Catalog scraper (`scrape_catalog_phase1.py`)
- [x] Database setup (`database.py`, `db_manager.py`)
- [x] Selector definitions (`iris_selectors.py`)
- [x] Configuration management (`config.py`)
- [x] SQLite database with projects table
- [x] 100+ projects captured

### Technical Achievements
- ✅ Successfully authenticated browser automation
- ✅ Dynamic pagination handling ("Cargar más" button)
- ✅ Robust wait strategy (polling vs wait_for_function)
- ✅ Duplicate prevention (UNIQUE constraint on detail_url)
- ✅ 129 unique projects captured in 11 iterations

### Challenges Overcome
1. **Wrong CSS selector** - `.table-row` → `a[href*='/proyecto/']`
2. **Timeout issues** - `wait_for_function()` → polling with `evaluate()`
3. **Dynamic loading** - Implemented custom wait logic for AJAX updates

### Metrics
```
Projects captured:    129
Iterations:           11
Success rate:         100%
Time per run:         ~3-4 minutes
Database size:        2.5 MB
```

---

## 🚧 Phase 2: Project Detail Scraping

**Status:** 🚧 **PLANNED** (Starting Feb 17, 2026)

### Objectives
For each project in the catalog, extract:
- Full project metadata (description, amenities, characteristics)
- Units table (apartments, offices, garages)
- Developer information (contact, assets)
- Downloadable files (brochures, floor plans, logos)

### Deliverables
- [ ] Detail scraper module (`scrape_project_details.py`)
- [ ] Units table parser (`scrape_units_table.py`)
- [ ] Developer info extractor (`scrape_developer_info.py`)
- [ ] Asset downloader (extend `downloader.py`)
- [ ] Extended database schema (units, developer_assets tables)
- [ ] Integration tests for detail scraping
- [ ] Error recovery & retry logic

### Implementation Plan

#### Step 1: Reconnaissance (2 days)
**Goal:** Understand project detail page structure

**Tasks:**
- [ ] Manually inspect 5-10 sample project detail pages
- [ ] Document units table structure and variations
- [ ] Identify "Más información" modal structure
- [ ] Map asset download URLs (PDFs, images)
- [ ] Document edge cases (projects with 0 units, missing assets)

**Deliverable:** `.ai/context/PHASE2_RESEARCH.md` with:
- CSS selectors for all elements
- Sample HTML snippets
- Edge case documentation

#### Step 2: Schema Extension (1 day)
**Goal:** Prepare database for Phase 2 data

**Tasks:**
- [ ] Create `units` table migration
- [ ] Create `developer_assets` table migration
- [ ] Add foreign key constraints
- [ ] Extend `projects` table with Phase 2 fields
- [ ] Write migration script

**Deliverable:** `migrations/002_phase2_schema.sql`

#### Step 3: Core Scraping Logic (3 days)
**Goal:** Implement detail page scraping

**Tasks:**
- [ ] Implement `scrape_project_details.py` main loop
- [ ] Parse units table with BeautifulSoup or Playwright selectors
- [ ] Handle different unit typologies (1BR, 2BR, garages, etc.)
- [ ] Extract price columns (cash, installments, list)
- [ ] Extract square meters (internal, external)
- [ ] Parse boolean flags (has_rent, has_360_view)

**Deliverable:** Functional scraper that processes 1 project end-to-end

#### Step 4: Developer Info & Assets (2 days)
**Goal:** Extract developer modal and download files

**Tasks:**
- [ ] Click "Más información" button
- [ ] Wait for modal to appear
- [ ] Extract developer name, contact info
- [ ] Identify asset URLs (brochure, memoria descriptiva, logo)
- [ ] Download PDFs to `assets/proyecto_{id}/` directory
- [ ] Store metadata in `developer_assets` table

**Deliverable:** Asset downloader with file organization

#### Step 5: Batch Processing & Error Handling (2 days)
**Goal:** Process all 129 projects robustly

**Tasks:**
- [ ] Implement retry logic (3 attempts with backoff)
- [ ] Add rate limiting (1-2s delay between requests)
- [ ] Log failed projects to `failed_projects.json`
- [ ] Add progress bar (tqdm)
- [ ] Implement `--resume` flag to continue interrupted runs
- [ ] Add `--limit N` flag for testing

**Deliverable:** Production-ready batch scraper

#### Step 6: Testing & Validation (2 days)
**Goal:** Ensure data quality and reliability

**Tasks:**
- [ ] Write unit tests for units table parser
- [ ] Write integration tests for full detail flow
- [ ] Validate data integrity (foreign keys, no nulls in required fields)
- [ ] Run full scrape on all 129 projects
- [ ] Verify assets downloaded correctly
- [ ] Generate summary report (N units, N assets, N failures)

**Deliverable:** Test suite with 80%+ coverage

### Technical Challenges

**Challenge 1: Dynamic Units Table Loading**
- **Issue:** Units table may load via AJAX after page render
- **Solution:** `await page.wait_for_selector('table.units-table', state='visible')`
- **Fallback:** Poll for table visibility with timeout

**Challenge 2: Modal Interaction**
- **Issue:** "Más información" modal requires click and wait
- **Solution:** 
  ```python
  await page.click('button:has-text("Más información")')
  await page.wait_for_selector('div.modal', state='visible')
  ```
- **Fallback:** Take screenshot if modal doesn't appear

**Challenge 3: Variable Unit Table Formats**
- **Issue:** Some projects have garages, some don't
- **Solution:** Parse table headers dynamically, adapt to columns present
- **Fallback:** Skip projects with unrecognized table structure, log for manual review

**Challenge 4: Asset Download Reliability**
- **Issue:** PDF URLs may 404 or require special headers
- **Solution:** Use Playwright's download API with proper context
- **Fallback:** Retry up to 3 times, log failures

**Challenge 5: Rate Limiting**
- **Issue:** Too many requests may trigger IP block
- **Solution:** Add 1-2 second delay between projects
- **Monitoring:** Watch for 429 status codes

### Success Criteria
- [ ] 95%+ projects successfully scraped
- [ ] Units extracted for all projects with units tables
- [ ] Assets downloaded for 80%+ projects
- [ ] No database integrity errors
- [ ] Run completes in under 4 hours
- [ ] Detailed error log for manual review of failures

### Estimated Timeline
**Total:** 12 days (2.5 weeks)
- Reconnaissance: 2 days
- Schema: 1 day
- Core logic: 3 days
- Assets: 2 days
- Batch processing: 2 days
- Testing: 2 days

---

## 🔮 Phase 3: Data Export & API

**Status:** 🔮 **FUTURE** (Week 3)

### Objectives
Make scraped data accessible via API and export formats.

### Deliverables
- [ ] REST API with FastAPI
- [ ] Endpoints:
  - `GET /projects` - List all projects
  - `GET /projects/{id}` - Project details with units
  - `GET /projects/{id}/units` - Units for project
  - `GET /projects/{id}/assets` - Assets for project
  - `GET /search?q={query}` - Full-text search
  - `GET /export/csv` - Export to CSV
  - `GET /export/json` - Export to JSON
- [ ] OpenAPI documentation (automatic with FastAPI)
- [ ] CSV/JSON export scripts
- [ ] Excel export with pandas

### Implementation Plan

#### API (FastAPI)
```python
# api.py
from fastapi import FastAPI, Query
from db_manager import get_all_projects, get_project_by_id

app = FastAPI(title="Irisbot API", version="1.0.0")

@app.get("/projects")
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    developer: str = None,
    zone: str = None
):
    """List projects with pagination and filters"""
    pass

@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    """Get project details with units"""
    pass

@app.get("/projects/{project_id}/units")
async def get_units(project_id: int):
    """Get units for a project"""
    pass
```

#### CSV Export
```python
# export_csv.py
import csv
from db_manager import get_all_projects

def export_projects_csv(output_path: str):
    projects = get_all_projects()
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=projects[0].keys())
        writer.writeheader()
        writer.writerows(projects)
```

#### Excel Export
```python
# export_excel.py
import pandas as pd
from db_manager import get_all_projects, get_all_units

def export_to_excel(output_path: str):
    projects = get_all_projects()
    units = get_all_units()
    
    with pd.ExcelWriter(output_path) as writer:
        pd.DataFrame(projects).to_excel(writer, sheet_name='Projects', index=False)
        pd.DataFrame(units).to_excel(writer, sheet_name='Units', index=False)
```

### Estimated Timeline
**Total:** 5 days
- API implementation: 2 days
- Export scripts: 1 day
- Documentation: 1 day
- Testing: 1 day

---

## 🔮 Phase 4: Production & Automation

**Status:** 🔮 **FUTURE** (Week 4)

### Objectives
Deploy to production environment with automated scheduling.

### Deliverables
- [ ] Dockerized application
- [ ] Automated daily/weekly scraping (cron/scheduler)
- [ ] Web dashboard (React/Vue) for browsing data
- [ ] Email notifications on scrape completion/failures
- [ ] Monitoring & alerting (Sentry, Datadog)
- [ ] Incremental updates (re-scrape only changed projects)
- [ ] PostgreSQL migration (optional, for scalability)

### Deployment Architecture
```
┌──────────────────────────────────────────────────────┐
│              Production Environment                   │
│                                                       │
│  ┌─────────────┐       ┌──────────────┐             │
│  │   Docker    │       │  PostgreSQL  │             │
│  │  Container  │──────▶│   Database   │             │
│  │  (Irisbot)  │       │              │             │
│  └─────────────┘       └──────────────┘             │
│         │                                             │
│         │ cron                                        │
│         ▼                                             │
│  ┌─────────────┐       ┌──────────────┐             │
│  │  Scheduler  │       │   FastAPI    │             │
│  │  (daily at  │       │     API      │             │
│  │   3:00 AM)  │       │              │             │
│  └─────────────┘       └──────────────┘             │
│                               │                       │
│                               ▼                       │
│                        ┌──────────────┐             │
│                        │  React App   │             │
│                        │  (Dashboard) │             │
│                        └──────────────┘             │
└──────────────────────────────────────────────────────┘
```

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application
COPY . .

# Run scraper
CMD ["python", "scrape_catalog_phase1.py"]
```

### Automated Scheduling (cron)
```bash
# Run daily at 3:00 AM
0 3 * * * cd /app/irisbot && /usr/bin/python scrape_catalog_phase1.py >> /var/log/irisbot.log 2>&1
```

### Dashboard Features
- **Project Browser:** Paginated list with filters (zone, developer, price range)
- **Search:** Full-text search across project names, descriptions
- **Detail View:** Project details with embedded units table
- **Analytics:** Charts (projects by zone, price distribution, etc.)
- **Export:** Download CSV/Excel from UI

### Monitoring
- **Sentry:** Error tracking and alerting
- **Logging:** Structured logs to file + stdout
- **Metrics:** Scrape duration, success rate, projects/units count
- **Alerts:** Email on failures, Slack notifications

### Estimated Timeline
**Total:** 7 days
- Dockerization: 1 day
- Automation setup: 1 day
- Dashboard (basic): 3 days
- Monitoring: 1 day
- Testing & deployment: 1 day

---

## 🔄 Incremental Updates (Future Enhancement)

### Problem
Full scrapes take 3-4 minutes (Phase 1) + 2-4 hours (Phase 2) per run.

### Solution: Differential Scraping
Track last scrape timestamp, only re-scrape changed projects.

#### Implementation
```sql
-- Add to projects table
ALTER TABLE projects ADD COLUMN last_scraped_at TIMESTAMP;
ALTER TABLE projects ADD COLUMN last_modified_at TIMESTAMP;

-- Update on each scrape
UPDATE projects 
SET last_scraped_at = CURRENT_TIMESTAMP 
WHERE id = ?;
```

#### Logic
```python
# 1. Scrape catalog
# 2. Compare with existing DB
# 3. Identify new/changed projects
# 4. Only scrape those in Phase 2

async def incremental_scrape():
    current_projects = await scrape_catalog()
    existing_projects = get_all_projects_from_db()
    
    # Find new projects
    new_urls = set(p['detail_url'] for p in current_projects) - \
               set(p['detail_url'] for p in existing_projects)
    
    # Find changed projects (e.g., price changed)
    changed = []
    for curr in current_projects:
        existing = get_project_by_url(curr['detail_url'])
        if existing and curr['price_from'] != existing['price_from']:
            changed.append(curr)
    
    # Scrape only new + changed
    to_scrape = list(new_urls) + changed
    logger.info(f"Incremental scrape: {len(to_scrape)} projects")
    
    for project in to_scrape:
        await scrape_project_details(project)
```

**Benefit:** Reduces Phase 2 time from 2-4 hours → 10-30 minutes for daily updates.

---

## 📊 Project Milestones

### Milestone 1: MVP ✅ COMPLETE
- [x] Phase 1 complete (catalog scraping)
- [x] 100+ projects in database
- [x] Core infrastructure working

**Achieved:** Feb 14, 2026

### Milestone 2: Full Data Extraction 🚧 IN PROGRESS
- [ ] Phase 2 complete (detail scraping)
- [ ] All units extracted
- [ ] Assets downloaded

**Target:** Feb 28, 2026

### Milestone 3: API & Export 🔮 FUTURE
- [ ] Phase 3 complete (API)
- [ ] CSV/JSON export working
- [ ] Basic analytics

**Target:** Mar 7, 2026

### Milestone 4: Production 🔮 FUTURE
- [ ] Phase 4 complete (automation)
- [ ] Deployed to production
- [ ] Dashboard live

**Target:** Mar 14, 2026

---

## 🎯 Success Metrics

### Phase 1 Metrics ✅ (Achieved)
- ✅ 129 projects captured (target: 90+)
- ✅ 100% success rate (target: 95%+)
- ✅ 0 duplicates (target: 0)
- ✅ 3-4 minutes per run (target: <5 min)

### Phase 2 Metrics 🚧 (Targets)
- 🎯 1000-2000 units extracted
- 🎯 95%+ project success rate
- 🎯 80%+ assets downloaded
- 🎯 <4 hours total scrape time

### Phase 3 Metrics 🔮 (Targets)
- 🎯 API responds in <100ms
- 🎯 CSV export in <5 seconds
- 🎯 Dashboard loads in <2 seconds

### Phase 4 Metrics 🔮 (Targets)
- 🎯 99%+ uptime
- 🎯 Daily scrapes complete successfully
- 🎯 Incremental updates in <30 minutes

---

## 🚀 Quick Start for New Developers

### Day 1: Setup
1. Clone repo: `git clone https://github.com/kikicarbonell/irisbot.git`
2. Install dependencies: `pip install -r requirements.txt && playwright install`
3. Create `.env` with credentials
4. Run Phase 1: `python scrape_catalog_phase1.py`
5. Verify database: `sqlite3 catalog_projects.db "SELECT COUNT(*) FROM projects;"`

### Day 2: Explore
1. Read [`.ai/context/PROJECT_OVERVIEW.md`](.ai/context/PROJECT_OVERVIEW.md)
2. Review [`.ai/context/ARCHITECTURE.md`](.ai/context/ARCHITECTURE.md)
3. Study [`scrape_catalog_phase1.py`](../../scrape_catalog_phase1.py)
4. Run tests: `pytest tests/`

### Day 3: Contribute
1. Check [`.ai/roadmap/ROADMAP.md`](.ai/roadmap/ROADMAP.md) (this file)
2. Pick a task from Phase 2 plan
3. Read [`.ai/guidelines/CODING_STANDARDS.md`](.ai/guidelines/CODING_STANDARDS.md)
4. Implement, test, submit PR

---

## 📚 Related Documentation

- [PROJECT_OVERVIEW.md](.ai/context/PROJECT_OVERVIEW.md) - High-level project description
- [ARCHITECTURE.md](.ai/context/ARCHITECTURE.md) - Technical architecture
- [DATA_MODEL.md](.ai/context/DATA_MODEL.md) - Database schemas
- [IMPLEMENTATION_STATUS.md](.ai/context/IMPLEMENTATION_STATUS.md) - Current state
- [CODING_STANDARDS.md](.ai/guidelines/CODING_STANDARDS.md) - Code conventions
- [SCRAPING_RULES.md](.ai/guidelines/SCRAPING_RULES.md) - Scraping best practices
- [README.md](../../README.md) - User guide

---

**Última actualización:** Febrero 16, 2026  
**Next Review:** Start of Phase 2 (Feb 17, 2026)
