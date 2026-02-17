# 📖 Irisbot Documentation Index

**Central hub para toda la documentación del proyecto Irisbot.**

**Última actualización:** Febrero 16, 2026  
**Cobertura de tests:** 91% ✅  
**Status:** Fase 1 Completa ✅ | Fase 2 Planeada 🚧

---

## 🏠 Quick Navigation

### Para Empezar
- **[README.md](../README.md)** — Descripción general del proyecto
- **[TESTING_QUICKSTART.md](../TESTING_QUICKSTART.md)** — Guía rápida para ejecutar tests (30 segundos)
- **[Makefile](../Makefile)** — Comandos útiles (`make help`)

### Para Desarrolladores
1. [CODING_STANDARDS.md](#coding_standards) — Estándares de código
2. [TESTING_GUIDE.md](#testing_guide) — Guía completa de testing
3. [CI_CD_PIPELINE.md](#ci_cd_pipeline) — Pipeline de GitHub Actions
4. [ARCHITECTURE.md](#architecture) — Arquitectura técnica
5. [DATA_MODEL.md](#data_model) — Esquema de base de datos

### Para Entender el Proyecto
1. [PROJECT_OVERVIEW.md](#project_overview) — Visión general y objetivos
2. [SCRAPING_RULES.md](#scraping_rules) — Reglas de scraping
3. [IMPLEMENTATION_STATUS.md](#implementation_status) — Estado actual
4. [ROADMAP.md](#roadmap) — Planificación de fases

---

## 📚 Documentación Completa

### Context (Contexto del Proyecto)

#### <a name="project_overview"></a> 📋 [PROJECT_OVERVIEW.md](context/PROJECT_OVERVIEW.md)
**Objetivo del Proyecto**

Qué es Irisbot, por qué existe, qué problemas resuelve.

- Descripción del proyecto y casos de uso
- Stack tecnológico (Python, Playwright, Selenium, SQLite)
- Objetivos de negocio y técnicos
- Métricas de éxito

**Leer si:** Quieres entender qué hace Irisbot y por qué

---

#### <a name="architecture"></a> 🏗️ [ARCHITECTURE.md](context/ARCHITECTURE.md)
**Arquitectura Técnica**

Cómo está construido Irisbot internamente.

- Componentes principales y relaciones
- Flujo de datos (pipeline de scraping)
- Patrones de diseño utilizados
- Integración con Iris portal

**Leer si:** Necesitas entender cómo funciona el código

---

#### <a name="data_model"></a> 📊 [DATA_MODEL.md](context/DATA_MODEL.md)
**Modelo de Datos**

Esquemas de base de datos y relaciones.

- Tablas SQLite y campos
- Relaciones entre entidades
- Constraints e índices
- Migraciones de schema

**Leer si:** Necesitas trabajar con la base de datos

---

#### <a name="implementation_status"></a> ✅ [IMPLEMENTATION_STATUS.md](context/IMPLEMENTATION_STATUS.md)
**Estado Actual del Proyecto**

Qué está hecho, qué está en progreso, qué falta.

- Fase 1 completa: 129 proyectos capturados ✅
- Fase 2 planeada: Scraping de detalles 🚧
- Métricas: 91% cobertura de tests, 83 tests
- Deuda técnica conocida
- Roadmap de próximas fases

**Leer si:** Quieres saber el estado actual y qué falta

---

### Guidelines (Guías de Desarrollo)

#### <a name="coding_standards"></a> 🎨 [CODING_STANDARDS.md](guidelines/CODING_STANDARDS.md)
**Estándares de Código**

Cómo escribir código en Irisbot.

- Convenciones de nombres
- Estructura de módulos
- Documentación con docstrings
- Manejo de errores
- Type hints y validación
- Restricciones del proyecto

**Leer si:** Vas a escribir código para el proyecto

---

#### <a name="testing_guide"></a> 🧪 [TESTING_GUIDE.md](guidelines/TESTING_GUIDE.md)
**Guía Completa de Testing**

Cómo escribir tests y mantener cobertura.

- Setup de entorno de testing
- Ejecutar tests (pytest, coverage)
- Escribir tests nuevos
- Mocking y fixtures
- Parametrización
- CI/CD pipeline

**Leer si:** Necesitas escribir tests o mejorar cobertura

---

#### <a name="ci_cd_pipeline"></a> 🔄 [CI_CD_PIPELINE.md](guidelines/CI_CD_PIPELINE.md)
**Pipeline de GitHub Actions**

Cómo funciona la validación automática.

- Triggers y workflow
- Matriz de pruebas (Python 3.10-3.13)
- Success/failure criteria
- Badges de status
- Simular pipeline localmente
- Troubleshooting

**Leer si:** Necesitas entender el CI pipeline o debuggear fallas

---

#### <a name="scraping_rules"></a> 🕷️ [SCRAPING_RULES.md](guidelines/SCRAPING_RULES.md)
**Reglas de Scraping**

Reglas específicas para scraping de Iris.

- Selectores CSS centralizados
- Tratamiento de casos edge
- Rate limiting y politeness
- Manejo de errores de scraping
- Logging y debugging

**Leer si:** Vas a trabajar en el scraper

---

#### <a name="ai_agent_guidelines"></a> 🤖 [AI_AGENT_GUIDELINES.md](guidelines/AI_AGENT_GUIDELINES.md)
**AI Agent Execution Guidelines**

Standards for AI-generated code and cleanup procedures.

- All code and documentation must be in English
- Temporary/intermediate files must be deleted after task completion
- Patterns of temporary files that should never be committed
- Verification checklist before finalizing tasks
- Integration with .gitignore for temporary files

**Read if:** You're setting up AI agentic code generation or reviewing AI-generated work

---

#### <a name="pre_commit"></a> 🪝 [PRE_COMMIT_SETUP.md](guidelines/PRE_COMMIT_SETUP.md)
**Pre-commit Hooks Configuration**

Automate code quality checks on every commit.

- Quick setup (make pre-commit-install)
- What gets checked (Code Review Checklist automation)
- All hooks explained (Black, isort, Flake8, mypy, pytest, custom)
- Common issues and solutions
- Configuration and customization

**Read if:** You're setting up the project or need to understand pre-commit validation

---

### Roadmap (Planificación)

#### <a name="roadmap"></a> 🗺️ [ROADMAP.md](roadmap/ROADMAP.md)
**Planificación de Fases**

Qué viene en las próximas versiones.

- Timeline de desarrollo
- Features planeadas
- Dependencias
- Riesgos identificados
- Métricas esperadas

**Leer si:** Quieres saber qué viene en el futuro

---

## 🔍 Buscar por Tema

### Authentication & Security
- [PROJECT_OVERVIEW.md - Autenticación](context/PROJECT_OVERVIEW.md#autenticación)
- [SCRAPING_RULES.md - Credenciales](guidelines/SCRAPING_RULES.md#credenciales)

### Database & Models
- [DATA_MODEL.md - Schema Completo](context/DATA_MODEL.md)
- [IMPLEMENTATION_STATUS.md - DB Setup](context/IMPLEMENTATION_STATUS.md#base-de-datos-sqlite)

### Testing & Quality
- [TESTING_GUIDE.md - Ejecutar Tests](guidelines/TESTING_GUIDE.md#ejecutar-tests)
- [TESTING_GUIDE.md - Escribir Tests](guidelines/TESTING_GUIDE.md#escribir-tests)
- [CI_CD_PIPELINE.md - GitHub Actions](guidelines/CI_CD_PIPELINE.md)

### Code Standards
- [CODING_STANDARDS.md - Convenciones](guidelines/CODING_STANDARDS.md#convenciones-de-nombres)
- [CODING_STANDARDS.md - Patrones](guidelines/CODING_STANDARDS.md#patrones-de-diseño)

### Scraping & Selectors
- [SCRAPING_RULES.md - Selectores](guidelines/SCRAPING_RULES.md#selectores-centralizados)
- [ARCHITECTURE.md - Pipeline](context/ARCHITECTURE.md#pipeline-de-scraping)

### Project Status
- [IMPLEMENTATION_STATUS.md - Phase 1](context/IMPLEMENTATION_STATUS.md#-phase-1-catalog-scraping---complete)
- [IMPLEMENTATION_STATUS.md - Testing](context/IMPLEMENTATION_STATUS.md#-testing-status---comprehensive)
- [ROADMAP.md - Timeline](roadmap/ROADMAP.md)

---

## 📊 Métricas en Vivo

```python
# Test Coverage
Total Tests:        83
Tests Passing:      ✅ 100%
Coverage:           91%
Target Coverage:    ≥ 90% ✅

# Code Size (Fase 1)
Total Files:        20+
Python Files:       12
Test Files:         9
Total LOC:          ~1800+
```

---

## 🚀 Flujo de Trabajo Recomendado

### 1️⃣ Nuevo Desarrollador
```
README.md →
TESTING_QUICKSTART.md →
CODING_STANDARDS.md →
PROJECT_OVERVIEW.md
```

### 2️⃣ Escribir Código Nuevo
```
CODING_STANDARDS.md →
ARCHITECTURE.md →
(escribir código) →
TESTING_GUIDE.md →
(escribir tests)
```

### 3️⃣ Debug de Tests
```
TESTING_GUIDE.md →
TESTING_QUICKSTART.md →
CI_CD_PIPELINE.md
```

### 4️⃣ Trabajo de Scraping
```
SCRAPING_RULES.md →
DATA_MODEL.md →
IMPLEMENTATION_STATUS.md
```

---

## 📞 Support

Si necesitas ayuda:

1. **¿Cómo ejecuto los tests?** → Ver [TESTING_QUICKSTART.md](../TESTING_QUICKSTART.md)
2. **¿Cómo escribo código?** → Ver [CODING_STANDARDS.md](guidelines/CODING_STANDARDS.md)
3. **¿Cómo escribo tests?** → Ver [TESTING_GUIDE.md](guidelines/TESTING_GUIDE.md)
4. **¿Cómo scraping funciona?** → Ver [SCRAPING_RULES.md](guidelines/SCRAPING_RULES.md)
5. **¿Cuál es el estado actual?** → Ver [IMPLEMENTATION_STATUS.md](context/IMPLEMENTATION_STATUS.md)

---

## 📝 Notas

- ✅ Toda la documentación está actualizada al Febrero 16, 2026
- ✅ Todos los ejemplos de código están probados
- 🔄 Se actualiza con cada release
- 📍 Versión: 1.0.0

---

**Última actualización:** Febrero 16, 2026
