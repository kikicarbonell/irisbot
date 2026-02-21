# PHASE 2 RECONNAISSANCE FINDINGS

## Status: 🚧 IN PROGRESS

**Document Purpose:** Map CSS selectors and data structures for project detail pages.

**Last Updated:** February 21, 2026

---

## 1. Target Page Structure

### URL Pattern
```
https://iris.infocasas.com.uy/proyecto/{project_id}
Example: https://iris.infocasas.com.uy/proyecto/100
```

### Page Layout (Expected)
```
┌─────────────────────────────────────────────────┐
│ Header (Project Title, Main Image)              │
├─────────────────────────────────────────────────┤
│ Metadata Section                                 │
│ - Location, Delivery Date, Status, Price        │
├─────────────────────────────────────────────────┤
│ Project Description                              │
├─────────────────────────────────────────────────┤
│ Units/Apartments Table                           │
├─────────────────────────────────────────────────┤
│ Amenities & Features                             │
├─────────────────────────────────────────────────┤
│ Developer Info (Button: "Más Información")      │
├─────────────────────────────────────────────────┤
│ Downloads (PDFs, Brochures)                     │
├─────────────────────────────────────────────────┤
│ Gallery/Images                                   │
└─────────────────────────────────────────────────┘
```

---

## 2. Project Metadata Extraction

### Fields to Extract
| Field | Expected Selector | Data Type | Notes |
|-------|------------------|-----------|-------|
| Project Name | `h1`, `.project-title` | Text | Main title |
| Description | `[class*='description']`, `p:first-of-type` | Text (500+ chars) | Long form |
| Zone/Location | `label:has-text('Zona')` + sibling | Text | Area name |
| Delivery Date | `label:has-text('Entrega')` + sibling | Date/Text | "Inmediata", "2025", etc |
| Status | `label:has-text('Estado')` + sibling | Select | Active, Pre-sale, etc |
| Price From | Already in Phase 1 | Number | Should verify/update |
| Developer | Already in Phase 1 | Text | Should verify/update |

### Sample Selector Patterns to Test
```html
<!-- Pattern 1: Label-Value pairs -->
<label>Zona:</label>
<span>Centro</span>

<!-- Pattern 2: Data attributes -->
<div data-field="zone">Centro</div>

<!-- Pattern 3: Bootstrap grid -->
<div class="row mb-3">
  <div class="col-md-6">
    <strong>Zona:</strong>
    <p>Centro</p>
  </div>
</div>

<!-- Pattern 4: Definition list -->
<dl>
  <dt>Zona</dt>
  <dd>Centro</dd>
</dl>
```

---

## 3. Units Table Analysis

### Critical: Table Structure Identification

#### Typical Column Headers
- Tipología (1 BR, 2 BR, Garage, etc)
- Superficie Interna (m²)
- Superficie Externa (m²)
- Desde (Price)
- Hasta (Price)
- En Alquiler (Yes/No)
- 360° View
- More Specs
- Actions (View Details)

#### Table Location
```
CSS Selectors to Test:
- table.units-table
- table[class*='unit'][class*='table']
- div[class*='table-responsive'] table
- div[role='table']
- [class*='apartments-table'], [class*='units-table']
```

#### Data Extraction Strategy
```python
{
  "type": "1 BR",          # Tipología
  "internal_sqm": 45.5,    # Superficie Interna
  "external_sqm": 10.2,    # Superficie Externa
  "price_from": 150000,    # Precio Desde (USD)
  "price_to": 180000,      # Precio Hasta
  "rent_available": true,  # En Alquiler
  "has_360": true,         # Vista 360°
  "status": "available"    # Estado
}
```

---

## 4. Developer Information Modal

### Interaction Flow
```
1. Find trigger: button:has-text("Más Información") or similar
2. Click button
3. Wait for modal: div[role='dialog'] or [class*='modal']
4. Extract modal content:
   - Company Name
   - Contact Email
   - Contact Phone
   - Company Description
   - Company Logo (if available)
5. Close modal (button:has-text("Cerrar"), ESC, click outside)
```

### Modal Selectors to Test
```
Role-based:
- [role='dialog']
- [role='alertdialog']

Class-based:
- .modal, .modal-content
- [class*='modal']
- [class*='offcanvas']

Custom:
- div:has(> button[aria-label='Close'])
- [class*='drawer'], [class*='sidebar']
```

### Developer Fields to Extract
```json
{
  "company_name": "Empresa XYZ",
  "contact_email": "info@empresa.com",
  "contact_phone": "+598 2 1234 5678",
  "website": "https://empresa.com.uy",
  "logo_url": "https://...",
  "description": "Specialized developer..."
}
```

---

## 5. Downloadable Assets

### Asset Types & Locations
| Asset Type | File Ext | Location | Field |
|------------|----------|----------|-------|
| Brochure | PDF | Project page | brochure_url |
| Floor Plans | PDF | Project page | floor_plans_url |
| Memoria Descriptiva | PDF | Project page | memoria_url |
| Logo | PNG/JPG | Modal | logo_url |
| Images | JPG/PNG | Gallery section | image_urls[] |

### Download Link Patterns
```html
<!-- Pattern 1: Direct href -->
<a href="/download/proyecto-235-brochure.pdf">Descargar Brochure</a>

<!-- Pattern 2: API endpoint -->
<a href="/api/proyecto/235/download/brochure">Descargar</a>

<!-- Pattern 3: External link -->
<a href="https://storage.example.com/brochures/proj-235.pdf">Descargar</a>

<!-- Pattern 4: Button styled -->
<button data-url="/files/proyecto-235.pdf">
  <i class="icon-download"></i> Descargar Brochure
</button>
```

### Asset Extraction Strategy
```python
{
  "project_id": 235,
  "files": [
    {
      "name": "brochure",
      "url": "https://iris.infocasas.com.uy/download/...",
      "type": "PDF",
      "size_mb": 2.5,
      "description": "Brochure del Proyecto"
    }
  ]
}
```

---

## 6. Edge Cases to Handle

### Case 1: Projects with No Units Table
**Scenario:** Special projects (land, commercial)
**Detection:** No table found OR table is empty
**Action:** Skip units extraction, log as "no_units_available"

### Case 2: Dynamic Loading
**Scenario:** Units table loads via AJAX after page render
**Detection:** Table selector returns null on first check
**Action:** Wait for table visibility, retry up to 3 times

### Case 3: Modal Not Opening
**Scenario:** Developer modal button exists but doesn't work
**Action:** Log error, skip developer info, continue with other fields

### Case 4: PDF Download Failures
**Scenario:** File URLs return 404 or require auth
**Action:** Retry up to 2 times, mark as "download_failed", continue

### Case 5: Missing Price Information
**Scenario:** Price shown as "Consultar", "POA", etc
**Action:** Store as null/unknown, flag for manual review

---

## 7. Selectors Priority (High → Low Confidence)

### High Priority (Most Likely to Work)
```css
/* Name/Title */
h1, h1.project-name, h1[class*='title']

/* Description */
[class*='description'], [class*='overview'], article p:nth-child(1)

/* Units Table */
table, table.units, table [class*='unit'], div[class*='table-responsive'] > table

/* Developer Button */
button:has-text('Más Información'), button:has-text('Desarrollador')

/* Assets */
a[href*='.pdf'], a[href*='.jpg'], [class*='download']
```

### Medium Priority
```css
/* With data attributes */
[data-field*='name'], [data-field*='title']

/* With role attributes */
[role='main'], [role='region']

/* Container based */
div[class*='section'], section
```

### Low Priority (Fallback)
```css
/* Generic */
div, p, span

/* Text matching */
:has-text('Zona'), :has-text('Precio')
```

---

## 8. Selectors to Test (Next Step)

### Manual Inspection Checklist
- [ ] Download actual project HTML (e.g., proyecto/100)
- [ ] Open in browser, inspect with DevTools
- [ ] Verify each selector category works:
  - [ ] Project metadata
  - [ ] Units table structure
  - [ ] Developer modal trigger
  - [ ] Asset download links
- [ ] Document any variations found
- [ ] Update selectors in code

### Code Testing Checklist
```python
# Test against real projects
test_projects = [100, 235, 236, 237, 238]

for project_id in test_projects:
    page = await browser.goto(f".../{project_id}")

    # Check each selector
    assert page.query_selector("h1") != None  # Title exists
    assert page.query_selector("table") != None  # Units table
    # ... etc
```

---

## 9. Implementation Priority

### Phase 2 Scraper Modules (Proposed Order)
1. **Base Scraper** (`scrape_project_details.py`)
   - Navigation to project page
   - Page wait/load logic
   - Error handling

2. **Project Metadata** (`extractors/metadata_extractor.py`)
   - Title, description
   - Status, delivery date, zone

3. **Units Table** (`extractors/units_extractor.py`)
   - Parse table structure
   - Extract rows
   - Handle variations

4. **Developer Info** (`extractors/developer_extractor.py`)
   - Modal interaction
   - Field extraction

5. **Assets** (`extractors/assets_extractor.py`)
   - Find download links
   - Prepare URLs for downloader

6. **Batch Processor** (`batch_scraper.py`)
   - Loop through projects
   - Retry logic
   - Progress tracking

---

## 10. Database Schema (Phase 2)

### New Tables Required

#### units Table
```sql
CREATE TABLE units (
    id TEXT PRIMARY KEY,
    project_id INTEGER NOT NULL,
    typology TEXT,
    internal_sqm REAL,
    external_sqm REAL,
    price_from INTEGER,
    price_to INTEGER,
    rent_available BOOLEAN,
    has_360_view BOOLEAN,
    status TEXT,
    scraped_at TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(project_id)
);
```

#### developer_assets Table
```sql
CREATE TABLE developer_assets (
    id TEXT PRIMARY KEY,
    project_id INTEGER NOT NULL,
    asset_type TEXT,
    file_url TEXT,
    local_path TEXT,
    file_size_mb REAL,
    download_status TEXT,
    downloaded_at TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(project_id)
);
```

#### projects_phase2 Fields (Extension)
```sql
ALTER TABLE projects ADD COLUMN IF NOT EXISTS:
    description TEXT,
    amenities TEXT,
    developer_name TEXT,
    developer_email TEXT,
    developer_phone TEXT,
    delivery_date TEXT,
    phase2_scraped_at TIMESTAMP,
    phase2_updated_at TIMESTAMP;
```

---

## Next Steps

1. ✅ Create this reconnaissance document
2. 📋 Download sample project HTML
3. ✅ Build selector test file
4. 🔍 Run manual validation on 5-10 projects
5. 📝 Document findings in detailed report
6. 💻 Implement extractors with validated selectors
7. 🧪 Create unit tests for each extractor
8. 🚀 Run batch scraper on all 129 projects

---

**Document Status:** READY FOR DATA COLLECTION
**Next Phase:** Execute reconnaissance script to gather real CSS selectors
