# AI DEVELOPMENT RULES & CONTEXT

## 1. Project Goal
Automatización de extracción de inventario inmobiliario (Scraping) del portal "Iris".
El objetivo es obtener precios, unidades y descargar assets (imágenes/PDFs) a disco local.

## 2. Tech Stack (Strict)
- **Lenguaje:** Python 3.10+
- **Browser Automation:** Playwright (Async API)
- **Database:** SQLite (usando `sqlite3` nativo o `SQLModel` si se requiere ORM simple).
- **HTTP Client:** `aiohttp` (para descarga eficiente de archivos binarios, NO usar requests síncrono).
- **File System:** `pathlib` (preferido sobre `os.path`).

## 3. Architecture Guidelines
- **Modularidad:** El código debe estar separado en:
  - `main.py`: Orquestador y lógica de Playwright.
  - `database.py`: Funciones CRUD.
  - `utils.py`: Descargas y manejo de archivos.
  - `config.py`: Constantes y secretos.
- **Async First:** Todo el I/O (Red y Disco) debe ser asíncrono (`async/await`).
- **Storage Structure:** `./data/{nombre_proyecto}/{numero_unidad}/`.

## 4. Coding Style
- Usar **Type Hinting** en todas las funciones (ej: `def funcion(x: int) -> str:`).
- Manejo de errores explícito: Usar `try/except` en bloques de red y loguear el error, no solo imprimirlo.
- Documentación: Docstrings estilo Google en funciones complejas.

## 5. Constraints
- **NO** usar Selenium.
- **NO** exponer credenciales en el código (usar variables de entorno o `config.py` en gitignore).
- Si el selector CSS falla, el script no debe romperse, debe loguear y continuar con la siguiente unidad.