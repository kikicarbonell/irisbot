"""utils.py — Async utilities (downloads and file handling).

Includes a function to download binary files using `aiohttp`.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import aiohttp

from config import DOWNLOAD_TIMEOUT_S, REQUEST_RETRY_BACKOFF_S, REQUEST_RETRY_COUNT, USER_AGENT

logger = logging.getLogger(__name__)


async def _fetch_with_retries(
    session: aiohttp.ClientSession, url: str, timeout: aiohttp.ClientTimeout
) -> Optional[bytes]:
    """Fetch URL with retry logic.

    Args:
        session: aiohttp ClientSession to use for requests.
        url: URL to fetch.
        timeout: aiohttp ClientTimeout object.

    Returns:
        Response body as bytes or None if all retries failed.
    """
    attempt = 0
    while attempt < REQUEST_RETRY_COUNT:
        try:
            async with session.get(url, timeout=timeout) as resp:
                resp.raise_for_status()
                return await resp.read()
        except Exception:
            attempt += 1
            backoff = REQUEST_RETRY_BACKOFF_S * attempt
            logger.warning(
                "Fetch failed (%s), attempt %d/%d — backoff %.1fs",
                url,
                attempt,
                REQUEST_RETRY_COUNT,
                backoff,
            )
            await asyncio.sleep(backoff)
    logger.error("Failed to fetch %s after %d attempts", url, REQUEST_RETRY_COUNT)
    return None


async def download_file(url: str, dest: Path) -> Optional[Path]:
    """Download a binary file to `dest` and return the full path or None on failure.

    Creates parent directory if needed.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT_S)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        data = await _fetch_with_retries(session, url, timeout)
        if data is None:
            return None
        tmp = dest.with_suffix(dest.suffix + ".part")
        try:
            tmp.write_bytes(data)
            tmp.replace(dest)
            return dest
        except Exception as exc:
            logger.exception("Error saving file %s: %s", dest, exc)
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            return None
