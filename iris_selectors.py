"""selectors.py — Centralizes CSS selectors from Iris for easy maintenance.

All CSS selectors for Iris components are here.
If Iris HTML structure changes, only update this file.
"""

from typing import Final

# ============================================================================
# AUTHENTICATION / LOGIN SELECTORS
# ============================================================================

# Email/user field
LOGIN_EMAIL_INPUT: Final[str] = "input[type='email'], input[name*='email' i], input[id*='email' i], input[placeholder*='email' i]"

# Password field
LOGIN_PASSWORD_INPUT: Final[str] = "input[type='password']"

# Submit/login button
LOGIN_SUBMIT_BUTTON: Final[str] = "button[type='submit'], button:has-text('Login'), button:has-text('Ingresar'), button:has-text('Entrar'), button:has-text('Iniciar'), form button"

# ============================================================================
# APARTMENT CATALOG SELECTORS
# ============================================================================

# Listing container (element that contains all items)
CATALOG_CONTAINER: Final[str] = "[class*='catalog'], [class*='listing'], [class*='grid'], main, article"

# Individual apartment card
APARTMENT_ITEM: Final[str] = "[class*='card'], [class*='item'], [class*='property'], [class*='apartment'], li[class*='property']"

# Apartment link (to access details)
APARTMENT_LINK: Final[str] = "a[href*='/property'], a[href*='/apartment'], a[href*='/propiedad']"

# ============================================================================
# APARTMENT DATA SELECTORS
# ============================================================================

# Apartment title/address
# Extended list of selectors with some attributes and fallbacks detected
# by the analyzer (includes images with `alt` as fallback when there's no text)
APARTMENT_TITLE: Final[str] = "h1, h2, h3, [class*='title'], [class*='address'], [class*='nombre'], [itemprop='name'], img[alt]"

# Price
# Added possible attributes and data-* where price is sometimes stored
APARTMENT_PRICE: Final[str] = "[class*='price'], [class*='precio'], [data-price], [data-price-raw], [itemprop='price'], span:has-text('$'), span:has-text('U$S')"

# Location/neighborhood
APARTMENT_LOCATION: Final[str] = "[class*='location'], [class*='address'], [class*='ubicacion'], [class*='barrio']"

# Bedrooms
APARTMENT_BEDROOMS: Final[str] = "[class*='bedroom'], [class*='dormitor'], [class*='hab']"

# Bathrooms
APARTMENT_BATHROOMS: Final[str] = "[class*='bathroom'], [class*='bath'], [class*='baño']"

# Area/floor space
APARTMENT_AREA: Final[str] = "[class*='area'], [class*='superficie'], [class*='m2']"

# Description
APARTMENT_DESCRIPTION: Final[str] = "[class*='description'], [class*='descripcion'], p"

# Images
APARTMENT_IMAGES: Final[str] = "img[src*='property'], img[alt*='property'], img[alt*='apartment']"

# ============================================================================
# PROJECT PAGE SELECTORS (CATALOG)
# ============================================================================

# Button to change to "List" view (table)
LIST_VIEW_BUTTON: Final[str] = "button:has-text('Lista'), [data-view='list'], [title*='Lista']"

# Project table in list view
PROJECT_TABLE: Final[str] = "table, [role='grid'], [class*='table'], [class*='projects-list']"

# Project row in table
PROJECT_ROW: Final[str] = "tbody tr, [role='row'], [class*='project-row'], tr[data-project-id]"

# Link/button to access project detail from row
PROJECT_DETAIL_LINK: Final[str] = "a[href*='/proyecto/'], a[href*='/proyectos/'], .project-link, [data-project-link]"

# ============================================================================
# PAGINATION SELECTORS
# ============================================================================

# "Load more" button
LOAD_MORE_BUTTON: Final[str] = "button:has-text('Cargar'), button:has-text('cargar'), button:has-text('Load more'), button:has-text('Ver más'), [class*='load-more'], [class*='ver-mas']"

# Loading indicator (spinner/skeleton)
LOADING_INDICATOR: Final[str] = "[class*='loading'], [class*='spinner'], [class*='skeleton'], [role='progressbar']"

# "No more items" message
NO_MORE_ITEMS_MESSAGE: Final[str] = "text=/no hay/i, text=/no more/i, text=/fin del listado/i"
