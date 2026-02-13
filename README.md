
# Irisbot — Scraper Iris (plantilla)

![CI](https://github.com/kikicarbonell/irisbot/actions/workflows/ci.yml/badge.svg)
![Codecov](https://codecov.io/gh/kikicarbonell/irisbot/branch/main/graph/badge.svg)

Pequeña plantilla para iniciar el scraper que automatiza extracción de inventario inmobiliario.

Requisitos mínimos
- Python 3.10+
- Instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ejecutar tests con resumen:

```bash
source .venv/bin/activate
python run_tests.py
```

Opciones útiles:

- Ejecutar sin listado por test:

```bash
python run_tests.py --no-list
```

- Ejecutar con cobertura y ver porcentaje al final:

```bash
python run_tests.py --with-coverage
```

- Elegir formato de cobertura (líneas o branches):

```bash
python run_tests.py --with-coverage --coverage-format branches
```

- Instalar navegadores de Playwright:

```bash
playwright install
```

Uso rápido

```bash
python main.py
```

Arquitectura refactorizada

### Módulos y responsabilidades:

- **`config.py`** — Constantes y configuración (variables de entorno).
- **`db_manager.py`** — Abstracción de la BD (init, insert_unit, fetch_unit) con inyección de `db_path`.
- **`downloader.py`** — Descarga de archivos con reintentos, async context manager para cierre automático de sesión.
- **`scraper.py`** — Orquestación de Playwright + DB + descargas. Permite inyectar `browser_factory`, `db_manager`, `downloader`.
- **`database.py`** — Funciones legadas (mantenidas para compatibilidad).
- **`utils.py`** — Utilidades generales (descargas simples sin reintentos).
- **`main.py`** — Punto de entrada; delega a `Scraper`.

### Inyección de dependencias:

Todos los módulos principales aceptan dependencias inyectables, lo que facilita:
- **Testing**: pasar mocks/fakes en lugar de implementaciones reales.
- **Flexibilidad**: cambiar comportamientos sin modificar código.
- **Desacoplamiento**: cada módulo es independiente y fácil de testear aisladamente.

Ejemplo con Scraper:

```python
from scraper import Scraper
from db_manager import DBManager
from downloader import Downloader
from pathlib import Path

# Uso normal (valores por defecto)
s = Scraper()
await s.run(["http://example.com/unit/1", "http://example.com/unit/2"])

# Uso con dependencias customizadas (tests/desarrollo)
db = DBManager(Path("/tmp/test.db"))
dl = Downloader()
s = Scraper(db_manager=db, downloader=dl)
await s.run(["http://example.com/unit/1"])

# Usar Downloader como context manager
async with Downloader() as dl:
    result = await dl.download("https://example.com/file.zip", Path("./file.zip"))
```

Notas
- No subir `config.py` con credenciales. Usa `.env` para secretos y añade a `.gitignore`.
- Revisa `AI_CONTEXT.md` para las reglas del proyecto (async, Playwright, SQLite).
- Coverage actual: **83%** (23 tests, todos pasando).
