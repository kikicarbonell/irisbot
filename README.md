
# Irisbot — Scraper Iris (plantilla)

<!-- REPLACE OWNER/REPO in the badge URL below with your GitHub repository -->
![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)

Pequeña plantilla para iniciar el scraper que automatiza extracción de inventario inmobiliario.

Requisitos mínimos
- Python 3.10+
- Instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Instalar navegadores de Playwright:

```bash
playwright install
```

Uso rápido

```bash
python main.py
```

Notas
- No subir `config.py` con credenciales. Usa `.env` para secretos y añade a `.gitignore`.
- Revisa `AI_CONTEXT.md` para las reglas del proyecto (async, Playwright, SQLite).
