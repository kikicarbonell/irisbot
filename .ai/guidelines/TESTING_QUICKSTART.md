# 🚀 Quick Start - Testing Guide

Quick guide to run tests in Irisbot.

## 30 seconds to run tests

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run tests
pytest tests/ -v
```

**Expected result:** ✅ 83 passed

---

## Most Common Commands

### View test coverage

```bash
pytest --cov=. --cov-report=term-missing tests/ -v
```

### Generate HTML coverage report

```bash
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html  # Ver en navegador
```

### Run only one test file

```bash
pytest tests/test_auth.py -v
```

### Run only one test function

```bash
pytest tests/test_auth.py::test_authenticate_success -v
```

### Tests in watch mode (re-run when files change)

```bash
pip install pytest-watch
ptw tests/ -- -v
```

---

## Con Makefile (Recomendado)

Si tienes `make` instalado (macOS/Linux), es más simple:

```bash
make test              # Ejecutar todos los tests
make test-cov          # Con reporte de cobertura
make test-cov-html     # Generar HTML y abrir en navegador
make coverage-check    # Verificar que sea ≥ 90%
make ci-local          # Simular CI pipeline localmente
```

Ver todos los comandos:
```bash
make help
```

---

## Interpretar Resultados

### ✅ Tests Correctos

```
======================= 83 passed in 30.53s ========================
```

Significa:
- ✅ Todos los 83 tests pasaron
- ⏱️ Tomó ~30 segundos
- 🎯 Cobertura: 91%

### ❌ Tests Fallidos

```
FAILED tests/test_auth.py::test_authenticate_success - AssertionError
======================= 1 failed, 82 passed in 28.51s ========================
```

Significa:
- ❌ 1 test falló
- ✅ 82 tests pasaron
- 🔍 Ver el error en la salida anterior

### ⚠️ Warnings (Ignorables)

```
RuntimeWarning: coroutine was never awaited
```

Estos warnings son normales y no afectan los tests. Son de la API de mocking async.

---

## Troubleshooting

### Error: "pytest not found"

```bash
pip install pytest pytest-cov
```

### Error: "playwright is not installed"

```bash
pip install playwright
python -m playwright install
```

### Tests lentos

Los tests tardan ~30 segundos porque incluyen tests async. Es normal.

Para correr rápido (sin captura de output):

```bash
pytest tests/ -v -s
```

### Coverage < 90%

Si la cobertura baja de 90%, necesitas agregar tests:

```bash
pytest --cov=. --cov-report=term-missing tests/
# Mira qué líneas no están cubiertas (columna "Missing")
```

---

## Métrica en Tiempo Real

```bash
# Verificar cobertura actual
pytest --cov=. --cov-report=term tests/ | grep TOTAL

# Resultado esperado:
# TOTAL                           1809    163    91%
```

---

## GitHub Actions (CI Automático)

Los tests se ejecutan automáticamente en:
- ✅ Cada push a `main` o `master`
- ✅ Cada pull request
- ✅ Sobre Python 3.10, 3.11, 3.12, 3.13

Ver status: https://github.com/kikicarbonell/irisbot/actions

---

## Documentación Completa

Para más detalles, ver: [.ai/guidelines/TESTING_GUIDE.md](.ai/guidelines/TESTING_GUIDE.md)

---

**Última actualización:** Febrero 16, 2026
