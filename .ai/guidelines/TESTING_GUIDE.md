# Testing Guide

**Última actualización:** Febrero 16, 2026  
**Cobertura actual:** 91% (83 tests, 0 fallos)

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Configuración del Entorno](#configuración-del-entorno)
3. [Ejecutar Tests](#ejecutar-tests)
4. [Generar Reportes](#generar-reportes)
5. [Escribir Tests](#escribir-tests)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Troubleshooting](#troubleshooting)

---

## Descripción General

### Objetivo

Mantener cobertura de tests **≥ 90%** para garantizar:
- ✅ Calidad de código
- ✅ Detección temprana de bugs
- ✅ Confianza en refactoring
- ✅ Documentación a través de tests

### Stack de Testing

| Herramienta | Versión | Propósito |
|-------------|---------|----------|
| `pytest` | 9.0.2 | Framework de testing |
| `pytest-cov` | 7.0.0 | Reporte de cobertura |
| `pytest-asyncio` | 1.3.0 | Tests de funciones async |
| `unittest.mock` | stdlib | Mocking de objetos |

### Métricas Actuales

```
Total statements:  1809
Covered:         1646
Missing:          163
Coverage:         91%
```

---

## Configuración del Entorno

### 1. Crear Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
pip install pytest-cov pytest-asyncio
```

### 3. Instalar Playwright

```bash
python -m playwright install chromium
```

### 4. Verificar Instalación

```bash
pytest --version
coverage --version
```

---

## Ejecutar Tests

### Opción 1: Ejecutar Todos los Tests

```bash
pytest tests/ -v
```

**Salida esperada:**
```
tests/test_auth.py ................ [ 20%]
tests/test_config.py ............. [ 25%]
tests/test_database.py ........... [ 27%]
tests/test_db_manager.py ......... [ 35%]
tests/test_downloader.py ......... [ 42%]
tests/test_iris_selectors.py .... [ 55%]
tests/test_main_extra.py ......... [ 60%]
tests/test_scrape_catalog.py .... [ 95%]
tests/test_utils.py ............. [100%]

====== 83 passed in 30.81s ======
```

### Opción 2: Ejecutar Tests Específicos

Por archivo:
```bash
pytest tests/test_auth.py -v
```

Por función:
```bash
pytest tests/test_auth.py::test_authenticate_success -v
```

Por patrón:
```bash
pytest tests/ -k "auth" -v
```

### Opción 3: Ejecutar con Output Detallado

Ver stdout/stderr:
```bash
pytest tests/ -v -s
```

Ver información de variables:
```bash
pytest tests/ -v --tb=long
```

### Opción 4: Ejecutar en Modo Watch

Instalar:
```bash
pip install pytest-watch
```

Ejecutar:
```bash
ptw tests/
```

---

## Generar Reportes

### Terminal Report

**Cobertura básica:**
```bash
pytest --cov=. tests/ -v
```

**Cobertura detallada con líneas faltantes:**
```bash
pytest --cov=. --cov-report=term-missing tests/ -v
```

**Cobertura por módulo:**
```bash
pytest --cov=. --cov-report=term-missing tests/ -v | grep -E "^(.*\.py|TOTAL)"
```

### HTML Report

Generar:
```bash
pytest --cov=. --cov-report=html tests/
```

Abrir en navegador:
```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### XML Report (para CI)

```bash
pytest --cov=. --cov-report=xml tests/
```

Esto crea `coverage.xml` que puede ser procesado por:
- Codecov
- SonarQube
- GitLab
- Azure DevOps

### JSON Report

```bash
pytest tests/ --json-report --json-report-file=report.json
```

---

## Escribir Tests

### Estructura Básica

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestMyFeature:
    """Tests para mi feature"""
    
    def test_simple_case(self):
        """Descripción clara del caso"""
        # Arrange
        data = {"key": "value"}
        
        # Act
        result = my_function(data)
        
        # Assert
        assert result is not None
        assert result['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_async_case(self):
        """Test para función async"""
        # Arrange
        mock_page = AsyncMock()
        
        # Act
        result = await my_async_function(mock_page)
        
        # Assert
        assert mock_page.evaluate.called
```

### Test Fixtures

```python
import pytest

@pytest.fixture
def database_connection():
    """Fixture que proporciona conexión a BD"""
    conn = setup_test_db()
    yield conn
    teardown_test_db(conn)

def test_database_insert(database_connection):
    """Test que usa la fixture"""
    database_connection.insert_record({"name": "Test"})
    result = database_connection.get_record("Test")
    assert result is not None
```

### Mocking

```python
from unittest.mock import AsyncMock, MagicMock, patch

# AsyncMock para funciones async
mock_page = AsyncMock()
mock_page.goto = AsyncMock()
await mock_page.goto("http://example.com")
mock_page.goto.assert_called_once()

# Patch para reemplazar imports
with patch('module.function', return_value="mocked"):
    result = module.function()
    assert result == "mocked"

# Mock con side_effect
mock = MagicMock()
mock.side_effect = [1, 2, 3]
assert mock() == 1
assert mock() == 2
```

### Parametrización

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("INMEDIATA", "inmediata"),
    ("MAYO 2026", "mayo 2026"),
    ("", None),
])
def test_parse_delivery(input, expected):
    """Test con múltiples casos"""
    result = parse_delivery(input)
    assert result == expected
```

### Markers para Organizacion

```python
# En pytest.ini está configurado:
[pytest]
markers =
    asyncio: mark test as async
    integration: mark test as integration test
    slow: mark test as slow
    unit: mark test as unit test

# Usar:
@pytest.mark.unit
def test_simple_logic():
    pass

@pytest.mark.integration
def test_with_real_db():
    pass

# Ejecutar solo unit tests:
pytest tests/ -m unit -v

# Ejecutar excluyendo slow tests:
pytest tests/ -m "not slow" -v
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

El pipeline se ejecuta automáticamente en cada push y PR:

**Archivo:** `.github/workflows/ci.yml`

### Pasos del Pipeline

1. **Checkout** — Descargar código
2. **Setup Python** — Instalar Python (múltiples versiones)
3. **Cache pip** — Cachear dependencias
4. **Install deps** — Instalar paquetes
5. **Install Playwright** — Instalar navegadores
6. **Run tests** — Ejecutar pytest
7. **Verify coverage** — Verificar ≥ 90%
8. **Upload reports** — Subir a Codecov
9. **Check status** — Fallar si tests fallan

### Configuración

```yaml
# Versiones de Python testeadas
python-version: ['3.10', '3.11', '3.12', '3.13']

# Threshold mínimo de cobertura
coverage report --fail-under=90

# Upload a Codecov
codecov/codecov-action@v4
```

### Status Badge

En README.md:
```markdown
![CI](https://github.com/kikicarbonell/irisbot/actions/workflows/ci.yml/badge.svg)
![Codecov](https://codecov.io/gh/kikicarbonell/irisbot/branch/main/graph/badge.svg)
```

### Configurar Codecov (Opcional)

1. Verificar [codecov.io](https://codecov.io)
2. Conectar repositorio
3. Copiar token en `CODECOV_TOKEN` secret
4. El pipeline subirá automáticamente

---

## Troubleshooting

### Error: "No module named pytest"

```bash
pip install pytest pytest-cov pytest-asyncio
```

### Error: "playwright is not installed"

```bash
pip install playwright
python -m playwright install
```

### Tests fallan solo en CI

Comprobar:
- ¿Versión diferente de Python?
- ¿Variables de entorno faltantes?
- ¿Playwright no instalado?

Solución:
```bash
# Local: simular CI
python3.13 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
pytest --cov=. tests/
```

### Cobertura no alcanza 90%

1. Identificar módulos sin cobertura:
```bash
pytest --cov=. --cov-report=term-missing tests/ | grep " 0%"
```

2. Ver líneas específicas sin cobertura:
```bash
pytest --cov=scrape_catalog_phase1 --cov-report=term-missing tests/
```

3. Añadir tests para esas líneas

### AsyncMock no funciona

```python
# ❌ Incorrecto
mock = Mock()
mock.evaluate = Mock(return_value=True)

# ✅ Correcto
mock = AsyncMock()
mock.evaluate = AsyncMock(return_value=True)
```

### Timeout en tests async

```python
@pytest.mark.asyncio
@pytest.mark.timeout(10)  # Timeout de 10 segundos
async def test_with_timeout():
    await slow_function()
```

---

## Best Practices

### ✅ Do's

- ✅ Escribir tests antes de código (TDD)
- ✅ Usar nombres descriptivos
- ✅ Un assert por test (idealmente)
- ✅ Testear casos edge
- ✅ Usar fixtures para setup común
- ✅ Documentar tests complejos
- ✅ Mantener tests rápidos (<1s cada uno)
- ✅ Verificar cobertura regularmente

### ❌ Don'ts

- ❌ Tests dependientes entre sí
- ❌ Usar datos hardcodeados
- ❌ Esperar tiempos innecesarios
- ❌ Incluir lógica de negocio en tests
- ❌ Olvidar cleanup de recursos
- ❌ Ignorar warnings de tests
- ❌ Hacer tests demasiado generales
- ❌ Saltarse tests "triviales"

---

## Recursos

- [pytest docs](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

---

## Contacto

Para dudas sobre testing, consulta la documentación de desarrollo en [`.ai/guidelines/`](.ai/guidelines/)
