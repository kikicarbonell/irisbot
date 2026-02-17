# PROJECT OVERVIEW - Irisbot

## 📋 Descripción del Proyecto

**Irisbot** es un scraper automatizado para extraer información de inventario inmobiliario de la plataforma **Iris PropertyTech** (https://iris.infocasas.com.uy).

### Objetivo Principal
Automatizar la extracción completa y estructurada de:
- **Catálogo de proyectos inmobiliarios** (edificios en construcción/venta)
- **Unidades individuales** (apartamentos, locales, garajes)
- **Metadata de desarrolladores** (contacto, assets, documentación)
- **Assets multimedia** (brochures PDF, planos, imágenes)

### Contexto de Negocio
Iris es una plataforma B2B para agentes inmobiliarios que requiere:
- 🔐 **Autenticación obligatoria** (email/password)
- 🌐 **SPA con contenido dinámico** (React/Vue con carga asíncrona)
- 📄 **Paginación progresiva** (botón "Cargar más")
- 🏗️ **Estructura jerárquica**: Proyecto → Unidades → Assets

---

## 🎯 Casos de Uso

### 1. Captura de Catálogo Completo (Fase 1 - ✅ Implementado)
- Autenticar en Iris
- Navegar al catálogo de proyectos
- Cargar TODOS los proyectos mediante paginación automática
- Almacenar información básica en base de datos SQLite

**Estado:** ✅ **COMPLETADO** (129 proyectos capturados)

### 2. Extracción de Detalles de Proyecto (Fase 2 - 🚧 Pendiente)
Para cada proyecto del catálogo:
- Navegar a URL de detalle
- Extraer metadata del proyecto
- Identificar y extraer tabla de unidades
- Capturar información del desarrollador
- Descargar assets opcionales

### 3. Scraping de Unidades Individuales (Fase 2 - 🚧 Pendiente)
Para cada unidad dentro de un proyecto:
- Capturar especificaciones técnicas
- Extraer precios (contado, plazo obra, lista)
- Identificar amenities y características
- Descargar planos/imágenes de referencia

---

## 🛠️ Stack Tecnológico

### Core
- **Python 3.10+** - Lenguaje base
- **Playwright** - Browser automation (headless/headful)
- **SQLite** - Base de datos local
- **asyncio** - Programación asíncrona

### Dependencias Clave
```txt
playwright>=1.40.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### Tools & CI/CD
- **pytest** - Testing framework
- **GitHub Actions** - CI/CD pipeline
- **codecov** - Code coverage tracking

---

## 📊 Arquitectura de Datos Iris

```
┌────────────────────────────────────────────────────────────┐
│              🔐 PORTAL IRIS (Autenticación)                │
│     https://iris.infocasas.com.uy/iniciar-sesion          │
└────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────┐
│           📋 CATÁLOGO DE PROYECTOS (Nivel 1)               │
│     https://iris.infocasas.com.uy/proyectos               │
│                                                             │
│  • Grid/List/Tabla de proyectos                            │
│  • Paginación: Botón "Cargar más"                          │
│  • Cada proyecto = 1 entidad comercial única               │
│  • Datos visibles:                                          │
│    - Nombre, Zona, Ubicación                               │
│    - Desarrollador, Comisión                               │
│    - Tipo de entrega, Estado del proyecto                  │
│    - Precio desde, Ley VP                                  │
└────────────────────────────────────────────────────────────┘
                           ↓
                  (Click en proyecto)
                           ↓
┌────────────────────────────────────────────────────────────┐
│          🏠 DETALLE DE PROYECTO (Nivel 2)                  │
│     https://iris.infocasas.com.uy/proyecto/{ID}           │
│                                                             │
│  📄 Información del Proyecto:                              │
│     • Descripción, Amenities                               │
│     • Características (plantas, unidades, garajes)         │
│     • Botón "Más información" → Modal con:                 │
│       - Brochure PDF                                       │
│       - Memoria descriptiva PDF                            │
│       - Logo desarrollador                                 │
│       - Contacto desarrollador                             │
│                                                             │
│  📊 Tabla de Unidades (tipologías):                        │
│     ├─ Monoambientes   (N unidades)                       │
│     ├─ Oficinas        (N unidades)                       │
│     ├─ 1 Dormitorio    (N unidades)                       │
│     ├─ 2 Dormitorios   (N unidades)                       │
│     ├─ 3 Dormitorios   (N unidades)                       │
│     └─ Garajes         (N unidades)                       │
│                                                             │
│     Columnas por unidad:                                   │
│     • Unidad: Número/ID                                    │
│     • Contado: Precio pago único                           │
│     • Plazo de obra: Precio con cuotas durante obra        │
│     • Precio de lista: Precio público                      │
│     • Internos: m² internos                                │
│     • Con renta: Sí/No                                     │
│     • Vista 360: Sí/No                                     │
└────────────────────────────────────────────────────────────┘
                           ↓
                  (Click en unidad)
                           ↓
┌────────────────────────────────────────────────────────────┐
│          🏢 DETALLE DE UNIDAD (Nivel 3 - Opcional)         │
│                                                             │
│  • Imágenes de referencia del apartamento                  │
│  • Planos (PDF/Imagen) de la unidad específica             │
│  • Tour virtual 360° (si disponible)                       │
└────────────────────────────────────────────────────────────┘
```

---

## 📈 Métricas del Proyecto

### Estado Actual (Fase 1 Completada)
- ✅ **129 proyectos** capturados en catálogo
- ✅ **Paginación automática** funcional
- ✅ **Base de datos** inicializada y poblada
- ✅ **11 iteraciones** de paginación exitosas
- ✅ **100% tasa de éxito** en autenticación

### Cobertura de Datos (Fase 1)
```
projects (tabla)
├─ id (PRIMARY KEY)
├─ name ✅
├─ zone ✅
├─ delivery_type ✅
├─ delivery_torres ✅
├─ project_status ✅
├─ price_from ✅
├─ developer ✅
├─ commission ✅
├─ has_ley_vp ✅
├─ location ✅
├─ image_url ✅
└─ detail_url ✅
```

### Próximos Hitos (Fase 2)
- 🎯 Scraping de 129 páginas de detalle de proyectos
- 🎯 Extracción de ~1000-2000 unidades estimadas
- 🎯 Descarga de assets multimedia (PDFs, imágenes)
- 🎯 Almacenamiento jerárquico en DB

---

## 🔐 Configuración Requerida

### Variables de Entorno (.env)
```bash
# Credenciales Iris
IRIS_EMAIL=usuario@ejemplo.com
IRIS_PASSWORD=contraseña_segura

# URLs base
IRIS_BASE_URL=https://iris.infocasas.com.uy
IRIS_LOGIN_URL=https://iris.infocasas.com.uy/iniciar-sesion
IRIS_CATALOG_URL=https://iris.infocasas.com.uy/proyectos?country=1&order=promos%2Cpopularity

# Configuración Playwright
PLAYWRIGHT_HEADLESS=True
PLAYWRIGHT_TIMEOUT_MS=30000

# Logging
LOG_LEVEL=INFO
```

---

## 🚀 Quick Start

### 1. Instalación
```bash
# Clonar repositorio
git clone https://github.com/kikicarbonell/irisbot.git
cd irisbot

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar navegadores Playwright
playwright install
```

### 2. Configuración
```bash
# Crear archivo .env con credenciales
cp .env.example .env
# Editar .env con tus credenciales de Iris
```

### 3. Ejecución
```bash
# Scraping de catálogo (Fase 1)
python scrape_catalog_phase1.py

# Ver resultados en DB
sqlite3 catalog_projects.db "SELECT COUNT(*) FROM projects;"
```

---

## 📚 Documentación Adicional

Para información más detallada, consultar:
- [`.ai/context/ARCHITECTURE.md`](.ai/context/ARCHITECTURE.md) - Arquitectura técnica detallada
- [`.ai/context/DATA_MODEL.md`](.ai/context/DATA_MODEL.md) - Esquemas de base de datos
- [`.ai/roadmap/ROADMAP.md`](.ai/roadmap/ROADMAP.md) - Planificación de fases
- [`README.md`](../../README.md) - Guía de uso general

---

**Última actualización:** Febrero 16, 2026
**Versión:** 1.0.0 (Fase 1 completa)
