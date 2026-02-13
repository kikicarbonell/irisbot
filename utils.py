"""utils.py — utilidades asíncronas (descargas y manejo de archivos).

Incluye una función para descargar archivos binarios usando `aiohttp`.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import aiohttp

from config import CONCURRENT_DOWNLOADS, DOWNLOAD_TIMEOUT_S, REQUEST_RETRY_COUNT, REQUEST_RETRY_BACKOFF_S, DATA_DIR, USER_AGENT

logger = logging.getLogger(__name__)


async def _fetch_with_retries(session: aiohttp.ClientSession, url: str, timeout: int) -> Optional[bytes]:
    attempt = 0
    while attempt < REQUEST_RETRY_COUNT:
        try:
            async with session.get(url, timeout=timeout) as resp:
                resp.raise_for_status()
                return await resp.read()
        except Exception as exc:
            attempt += 1
            backoff = REQUEST_RETRY_BACKOFF_S * attempt
            logger.warning("Fetch failed (%s), attempt %d/%d — backoff %.1fs", url, attempt, REQUEST_RETRY_COUNT, backoff)
            await asyncio.sleep(backoff)
    logger.error("Failed to fetch %s after %d attempts", url, REQUEST_RETRY_COUNT)
    return None


async def download_file(url: str, dest: Path) -> Optional[Path]:
    """Descarga un archivo binario a `dest` y devuelve la ruta completa o None en fallo.

    Crea el directorio padre si es necesario.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT_S)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        data = await _fetch_with_retries(session, url, timeout=DOWNLOAD_TIMEOUT_S)
        if data is None:
            return None
        tmp = dest.with_suffix(dest.suffix + ".part")
        try:
            tmp.write_bytes(data)
            tmp.replace(dest)
            return dest
        except Exception as exc:
            logger.exception("Error guardando archivo %s: %s", dest, exc)
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            return None
