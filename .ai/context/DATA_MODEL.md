# DATA MODEL - Irisbot Database Schemas

## 🗄️ Database: catalog_projects.db (SQLite)

---

## 📋 Phase 1: Projects (Current Schema)

### Table: `projects`

**Purpose:** Stores catalog-level information for each property development project

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

### Field Descriptions

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | INTEGER | NO | Auto-incremented primary key | `1` |
| `name` | TEXT | NO | Project name | `"Torre Vista"` |
| `zone` | TEXT | YES | Geographic zone/neighborhood | `"Pocitos"` |
| `delivery_type` | TEXT | YES | Delivery timeline | `"2025"`, `"Inmediata"` |
| `delivery_torres` | TEXT | YES | Tower delivery phases if multi-phase | `"Torre 1: 2024, Torre 2: 2025"` |
| `project_status` | TEXT | YES | Current project status | `"En construcción"`, `"Entrega inmediata"` |
| `price_from` | TEXT | YES | Starting price (parsed as text) | `"USD 120.000"` |
| `developer` | TEXT | YES | Developer/builder company | `"Desarrolladora XYZ"` |
| `commission` | TEXT | YES | Agent commission percentage | `"3%"`, `"4%"` |
| `has_ley_vp` | BOOLEAN | NO | Has "Ley de Vivienda Promovida" tax benefits | `1`, `0` |
| `location` | TEXT | YES | Address or location description | `"21 de Setiembre y Rbla."` |
| `image_url` | TEXT | YES | Main project image URL | `"https://..."` |
| `detail_url` | TEXT | NO (UNIQUE) | URL to project detail page | `"/proyecto/235"` |
| `scraped_at` | TIMESTAMP | NO | Timestamp when record was created | `2026-02-14 02:31:58` |

### Indexes
```sql
-- Unique constraint on detail_url prevents duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_detail_url ON projects(detail_url);

-- Optional performance indexes (add if needed)
CREATE INDEX IF NOT EXISTS idx_projects_developer ON projects(developer);
CREATE INDEX IF NOT EXISTS idx_projects_zone ON projects(zone);
```

### Constraints
- `detail_url` must be UNIQUE (prevents duplicate projects)
- `name` is NOT NULL (every project must have a name)

---

## 🏗️ Phase 2: Planned Schema Extensions

### Table: `units` (Future)

**Purpose:** Stores individual apartment/office/garage units within projects

```sql
CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    unit_number TEXT,
    typology TEXT,
    price_cash REAL,
    price_installments REAL,
    price_list REAL,
    sqm_internal REAL,
    sqm_external REAL,
    has_rent BOOLEAN DEFAULT 0,
    has_360_view BOOLEAN DEFAULT 0,
    floor TEXT,
    orientation TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

### Field Descriptions (units)

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `project_id` | INTEGER | NO | Foreign key to `projects.id` | `5` |
| `unit_number` | TEXT | YES | Unit identifier (e.g., "101", "A-302") | `"101"` |
| `typology` | TEXT | YES | Unit type | `"1 Dormitorio"`, `"Monoambiente"`, `"Garaje"` |
| `price_cash` | REAL | YES | Cash payment price (USD) | `125000.00` |
| `price_installments` | REAL | YES | Installment payment price (USD) | `135000.00` |
| `price_list` | REAL | YES | List/public price (USD) | `140000.00` |
| `sqm_internal` | REAL | YES | Internal square meters | `45.5` |
| `sqm_external` | REAL | YES | Balcony/terrace square meters | `8.2` |
| `has_rent` | BOOLEAN | NO | Unit has guaranteed rental income | `1`, `0` |
| `has_360_view` | BOOLEAN | NO | Has virtual 360° tour available | `1`, `0` |
| `floor` | TEXT | YES | Floor number | `"3"`, `"PB"`, `"10"` |
| `orientation` | TEXT | YES | Cardinal orientation | `"Norte"`, `"Sur"` |

### Indexes (units)
```sql
CREATE INDEX IF NOT EXISTS idx_units_project_id ON units(project_id);
CREATE INDEX IF NOT EXISTS idx_units_typology ON units(typology);
CREATE INDEX IF NOT EXISTS idx_units_price_cash ON units(price_cash);
```

---

### Table: `developer_assets` (Future)

**Purpose:** Stores downloadable files (PDFs, images) associated with projects

```sql
CREATE TABLE IF NOT EXISTS developer_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    asset_type TEXT NOT NULL,
    file_url TEXT,
    local_path TEXT,
    file_size_bytes INTEGER,
    downloaded_at TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

### Field Descriptions (developer_assets)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `asset_type` | TEXT | Type of asset | `"brochure"`, `"memoria"`, `"logo"`, `"floor_plan"` |
| `file_url` | TEXT | Original URL | `"https://iris.../brochure.pdf"` |
| `local_path` | TEXT | Path where file was saved locally | `"assets/proyecto_235/brochure.pdf"` |
| `file_size_bytes` | INTEGER | Size in bytes | `2048576` |
| `downloaded_at` | TIMESTAMP | When file was downloaded | `2026-02-15 10:30:00` |

---

## 📊 Data Model Relationships

```
projects (1)
    ├─── units (Many)
    │       └── One project has many units (apartments, offices, garages)
    │
    └─── developer_assets (Many)
            └── One project has many assets (brochures, floor plans, logos)
```

### Entity-Relationship Diagram

```
┌─────────────────────┐
│     projects        │
│─────────────────────│
│ id (PK)             │
│ name                │
│ zone                │
│ delivery_type       │
│ developer           │
│ detail_url (UNIQUE) │
│ ...                 │
└─────────────────────┘
          │
          │ 1
          │
          ├────────────────────┐
          │                    │
          │ N                  │ N
          ↓                    ↓
┌─────────────────┐   ┌──────────────────────┐
│     units       │   │  developer_assets    │
│─────────────────│   │──────────────────────│
│ id (PK)         │   │ id (PK)              │
│ project_id (FK) │   │ project_id (FK)      │
│ unit_number     │   │ asset_type           │
│ typology        │   │ file_url             │
│ price_cash      │   │ local_path           │
│ ...             │   │ ...                  │
└─────────────────┘   └──────────────────────┘
```

---

## 🔄 Data Flow & Extraction Strategy

### Phase 1: Catalog Scraping ✅ (Implemented)
```
Iris Catalog Page
        ↓
  Extract <a href*='/proyecto/'>
        ↓
  Parse card data (name, zone, price...)
        ↓
  INSERT INTO projects
```

### Phase 2: Detail Page Scraping 🚧 (Planned)
```
For each project in catalog_projects.db:
    Navigate to detail_url
        ↓
    Extract units table
        ↓
    FOR EACH unit row:
        INSERT INTO units (project_id, unit_number, typology, prices...)
        ↓
    Click "Más información" button
        ↓
    Extract developer info modal
        ↓
    Download brochure, memoria, logo
        ↓
    INSERT INTO developer_assets
```

---

## 📐 Data Type Decisions

### Why TEXT for prices instead of REAL?
**Rationale:**
- Prices might include currency symbols: `"USD 120.000"`
- Some prices are ranges: `"Desde USD 100.000"`
- Decimal separator varies by locale: `120.000` vs `120,000`
- Easier to parse later with `parse_price()` utility

**Future:** In Phase 2, `units.price_*` will use `REAL` for numerical operations.

### Why BOOLEAN as INTEGER (0/1)?
**Rationale:**
- SQLite doesn't have native BOOLEAN type
- Uses `0` = False, `1` = True
- Standard SQLite convention

### Why TIMESTAMP as TEXT?
**Rationale:**
- SQLite stores timestamps as ISO 8601 strings: `"2026-02-14 02:31:58"`
- `CURRENT_TIMESTAMP` function generates this format automatically
- Easily comparable with string operators (`>`, `<`)

---

## 🧹 Data Cleaning Rules

### Normalization Standards

**1. Prices:**
- Input: `"USD 125.000"`, `"U$S 125000"`, `"125.000 USD"`
- Output: `125000.0` (float, no symbols)

**2. Boolean Fields:**
- Input: `"Sí"`, `"Yes"`, `"✓"`, `true`
- Output: `1`
- Input: `"No"`, `None`, `""`, `false`
- Output: `0`

**3. URLs:**
- Always store as absolute paths: `"/proyecto/235"` ✅
- NOT relative: `"proyecto/235"` ❌
- Base URL concatenation happens at runtime

**4. Text Fields:**
- Strip leading/trailing whitespace
- Convert multiple spaces to single space
- Handle NULL vs empty string consistently

---

## 📈 Expected Data Volume

### Current State (Phase 1)
- **129 projects** in catalog
- **~20 KB** per project record
- **Total DB size:** ~2.5 MB

### Projected (Phase 2)
- **~1000-2000 units** (avg 10-15 units per project)
- **~300 assets** (PDFs, images)
- **Estimated DB size:** ~50-100 MB (with assets metadata)
- **Estimated files on disk:** ~500 MB - 1 GB (downloaded PDFs/images)

---

## 🔍 Sample Queries

### Get all projects by developer
```sql
SELECT * FROM projects 
WHERE developer LIKE '%Desarrolladora XYZ%'
ORDER BY scraped_at DESC;
```

### Count projects by zone
```sql
SELECT zone, COUNT(*) as count 
FROM projects 
GROUP BY zone 
ORDER BY count DESC;
```

### Find projects with Ley VP benefits
```sql
SELECT name, zone, price_from 
FROM projects 
WHERE has_ley_vp = 1;
```

### Get all units for a project (Phase 2)
```sql
SELECT u.* 
FROM units u
JOIN projects p ON u.project_id = p.id
WHERE p.name = 'Torre Vista'
ORDER BY u.price_cash ASC;
```

### Find units under USD 150k (Phase 2)
```sql
SELECT p.name, u.unit_number, u.typology, u.price_cash
FROM units u
JOIN projects p ON u.project_id = p.id
WHERE u.price_cash < 150000
ORDER BY u.price_cash ASC;
```

---

## 🛡️ Data Integrity Constraints

### Enforced Constraints
1. **Unique detail_url** - Prevents duplicate project scrapes
2. **NOT NULL on name** - Every project must have a name
3. **Foreign keys** (Phase 2) - Units/Assets must belong to valid project
4. **ON DELETE CASCADE** (Phase 2) - Deleting project removes all units/assets

### Validation Rules (Application Layer)
1. Validate URLs before insertion
2. Check price format before saving
3. Verify project_id exists before inserting units
4. Ensure asset files exist before marking as downloaded

---

**Última actualización:** Febrero 16, 2026
