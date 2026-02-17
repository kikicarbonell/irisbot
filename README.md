
# Irisbot — Iris Real Estate Inventory Scraper

![CI](https://github.com/kikicarbonell/irisbot/actions/workflows/ci.yml/badge.svg)
![Codecov](https://codecov.io/gh/kikicarbonell/irisbot/branch/main/graph/badge.svg)

**Automated scraper** to extract complete information about real estate projects from the [Iris PropertyTech](https://iris.infocasas.com.uy) platform.

**Current status:** ✅ **Phase 1 complete** (129 projects captured) | 🚧 **Phase 2 in planning** (detailed scraping)

---

## 🚀 Quick Start

### 1. Clone and install
```bash
git clone https://github.com/kikicarbonell/irisbot.git
cd irisbot
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### 2. Configure credentials
Create a `.env` file in the root directory:
```bash
IRIS_EMAIL=your_email@example.com
IRIS_PASSWORD=your_password
IRIS_BASE_URL=https://iris.infocasas.com.uy
PLAYWRIGHT_HEADLESS=True
```

### 3. Run catalog scraper (Phase 1)
```bash
python -m src.scrape_catalog_phase1
```

This command:
- Authenticates in Iris
- Loads all projects with automatic pagination
- Saves data in `catalog_projects.db`

### 4. Verify results
```bash
sqlite3 catalog_projects.db "SELECT COUNT(*) FROM projects;"
# Expected result: 129 projects
```

---

## 📚 Complete Documentation

For detailed project information, consult the documentation in the [`.ai/`](.ai/) directory:

### Project Context
- [**PROJECT_OVERVIEW.md**](.ai/context/PROJECT_OVERVIEW.md) - Overview, objectives and metrics
- [**ARCHITECTURE.md**](.ai/context/ARCHITECTURE.md) - Technical architecture and data flow
- [**DATA_MODEL.md**](.ai/context/DATA_MODEL.md) - Database schemas and relationships
- [**IMPLEMENTATION_STATUS.md**](.ai/context/IMPLEMENTATION_STATUS.md) - Current status and progress (includes testing metrics)

### Development Guides
- [**CODING_STANDARDS.md**](.ai/guidelines/CODING_STANDARDS.md) - Code standards and best practices
- [**SCRAPING_RULES.md**](.ai/guidelines/SCRAPING_RULES.md) - Specific scraping rules
- [**TESTING_GUIDE.md**](.ai/guidelines/TESTING_GUIDE.md) - Complete testing guide

### Planning
- [**ROADMAP.md**](.ai/roadmap/ROADMAP.md) - Phase planning and next steps

### Quick References
- [**TESTING_QUICKSTART.md**](TESTING_QUICKSTART.md) - Quick guide (30 sec to run tests)
- [**Makefile**](Makefile) - Available commands with `make help`

---

## 🧪 Testing

The project has **83 tests** covering **91% of the code**.

### Run Tests

**Option 1: With make (recommended)**
```bash
make test              # Run all tests
make test-cov          # With coverage report
make test-cov-html     # Generate HTML coverage report
make test-watch        # Tests in watch mode
```

**Option 2: With pytest directly**
```bash
source .venv/bin/activate
pytest tests/ -v       # All tests
pytest --cov=src --cov-report=term-missing tests/ -v  # With coverage
pytet --cov=src --cov-report=html tests/             # HTML report
```

### Generate Coverage Report

**Coverage with terminal report:**
```bash
pytest --cov=src --cov-report=term-missing tests/
```

**Cobertura con reporte HTML:**
```bash
pytest --cov=src --cov-report=html tests/
# Abrir htmlcov/index.html en el navegador
```

**Cobertura con reporte XML (para CI):**
```bash
pytest --cov=src --cov-report=xml --cov-report=term tests/
```

### Métricas de Testing

| Métrica | Valor |
|---------|-------|
| **Tests totales** | 83 |
| **Cobertura global** | 91% |
| **Tests pasando** | ✅ 100% |
| **Módulos cubiertos** | 20 |

#### Cobertura por Módulo

| Módulo | Cobertura |
|--------|----------:|
| `iris_selectors.py` | 100% |
| `test_utils.py` | 100% |
| `test_config.py` | 100% |
| `test_database.py` | 100% |
| `test_db_manager.py` | 100% |
| `test_scrape_catalog.py` | 99% |
| `test_downloader.py` | 99% |
| `test_auth.py` | 96% |
| `test_iris_selectors.py` | 97% |
| `utils.py` | 93% |
| `database.py` | 94% |
| `config.py` | 91% |
| `downloader.py` | 91% |
| `db_manager.py` | 89% |
| `auth.py` | 82% |
| `scrape_catalog_phase1.py` | 67% |

### Tests por Categoría

- **Autenticación** (`test_auth.py`): 7 tests
- **Selectores CSS** (`test_iris_selectors.py`): 10 tests
- **Scraper de catálogo** (`test_scrape_catalog.py`): 43 tests
  - Extracción de datos (list/table/grid views)
  - Parsing de delivery e info de proyecto
  - Funciones de scroll y navegación
  - Paginación y "Cargar más"
  - Migración de schema de BD
- **Configuración** (`test_config.py`): 1 test
- **Base de datos** (`test_database.py`, `test_database_extra.py`): 3 tests
- **DB Manager** (`test_db_manager.py`): 3 tests
- **Descarga de archivos** (`test_downloader.py`): 5 tests
- **Utilidades** (`test_utils.py`, `test_utils_extra.py`, `test_utils_more.py`): 5 tests
- **Edge cases** (`test_main_extra.py`): tests adicionales

### CI/CD Pipeline

Los tests se ejecutan automáticamente en cada push y pull request via GitHub Actions:

- Múltiples versiones de Python: 3.10, 3.11, 3.12, 3.13
- `pytest --cov=. --cov-report=xml --cov-report=term tests/`
- Verificación de threshold mínimo: 90%
- Upload automático a Codecov para tracking histórico

**Ver más:** [.ai/guidelines/TESTING_GUIDE.md](.ai/guidelines/TESTING_GUIDE.md)
- **Configuración** (`test_config.py`): 1 test
- **Base de datos** (`test_database.py`, `test_database_extra.py`): 3 tests
- **DB Manager** (`test_db_manager.py`): 3 tests
- **Descarga de archivos** (`test_downloader.py`): 5 tests
- **Utilidades** (`test_utils.py`, `test_utils_extra.py`, `test_utils_more.py`): 5 tests
- **Edge cases** (`test_main_extra.py`): tests adicionales

### CI/CD

Los tests se ejecutan automáticamente en cada push y pull request via GitHub Actions:

```yaml
# Ver .github/workflows/ci.yml para configuración completa
- pytest --cov=. --cov-report=xml --cov-report=term tests/
- Verificación de threshold mínimo: 90%
- Upload a Codecov para tracking histórico
```

---

## 🏗️ Arquitectura del Proyecto

### Módulos Principales (Fase 1)
- **`scrape_catalog_phase1.py`** — Scraper principal para catálogo de proyectos
- **`auth.py`** — Autenticación en portal Iris
- **`config.py`** — Configuración y variables de entorno
- **`database.py`** — Esquema de base de datos
- **`db_manager.py`** — Operaciones CRUD
- **`iris_selectors.py`** — Selectores CSS centralizados
- **`utils.py`** — Funciones auxiliares

### Base de Datos (SQLite)
**Archivo:** `catalog_projects.db`

**Tabla actual:** `projects` (129 registros)
- Información básica de cada proyecto: nombre, zona, precio, desarrollador, comisión, etc.

**Future tables (Phase 2):**
- `units` — Individual units (apartments, offices, garages)
- `developer_assets` — Downloaded assets (brochures, plans, logos)

---

## 📊 Project Status

### ✅ Phase 1 Complete
- [x] Iris authentication
- [x] Complete catalog scraping (129 projects)
- [x] Automatic pagination handling
- [x] Functional SQLite database
- [x] Unit and integration tests

### 🚧 Phase 2 Planned (Coming Soon)
- [ ] Project detail page scraping
- [ ] Units table extraction
- [ ] Asset downloads (PDFs, images)
- [ ] Developer information

### 🔮 Phase 3 Future
- [ ] REST API with FastAPI
- [ ] Export to CSV/JSON/Excel
- [ ] Web dashboard for data queries

---

## 🔍 Code Quality

The project uses **automated code quality checks** (`pre-commit`) that run on every commit and in the CI pipeline.

### Setup Code Quality (First Time)
```bash
make install-dev              # Install dev dependencies + pre-commit
make pre-commit-install       # Setup git hooks
```

### What Gets Checked
- ✅ **Code formatting** (Black, isort)
- ✅ **PEP 8 compliance** (Flake8)
- ✅ **Type hints** (mypy)
- ✅ **Docstrings** (pydocstyle)
- ✅ **Project constraints** (No Selenium, no hardcoded data)
- ✅ **Imports organization**
- ✅ **File integrity** (EOF, trailing whitespace, merge conflicts)

### Pre-commit in CI
The CI pipeline (`.github/workflows/ci.yml`) runs **the same pre-commit validation** as local development:
```bash
pre-commit run --all-files
```

This ensures consistency between local commits and remote validation.

**Full CI workflow includes:**
1. Pre-commit validation (code quality checks)
2. Test execution (pytest with coverage)
3. Coverage verification (90% minimum)
4. Support for Python 3.10, 3.11, 3.12, 3.13

**See also:** [Pre-commit Setup Guide](.ai/guidelines/PRE_COMMIT_SETUP.md)

---

## 🤝 Contributing

1. **Setup development environment:**
   ```bash
   make install-dev              # Install all dependencies
   make pre-commit-install       # Setup code quality hooks
   ```

2. **Create a branch for your feature:**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Commit your changes** (pre-commit validation runs automatically):
   ```bash
   git add .
   git commit -m 'Add amazing feature'  # Pre-commit hooks validate here
   ```

4. **If there are failures**, fix issues and retry:
   ```bash
   # Pre-commit shows exactly what needs fixing
   # Most issues can be auto-fixed by running:
   make format               # Auto-format with Black and isort

   # Then retry the commit
   git commit -m 'Add amazing feature'
   ```

5. **Push to your branch:**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request** (CI will validate again)

**Important:**
- ✅ All code quality checks must pass locally before pushing
- ✅ All tests must pass (automated in CI)
- ✅ Coverage must maintain 90%+ (checked in CI)
- ✅ Follow [CODING_STANDARDS.md](.ai/guidelines/CODING_STANDARDS.md)

---

## 📝 Important Notes

- ⚠️ **Never commit credentials:** Use `.env` for secrets and add it to `.gitignore`
- 📚 **Complete documentation:** Check [`.ai/`](.ai/) for detailed guides
- 🧪 **Testing:** All PRs must include tests
- 🎨 **Standards:** Follow [CODING_STANDARDS.md](.ai/guidelines/CODING_STANDARDS.md)

---

## 📄 License

This project is open source. Check the `LICENSE` file for details.

---

**Last updated:** February 16, 2026
