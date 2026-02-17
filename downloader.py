"""downloader.py — Encapsulates file download logic.

Separates retries and error handling, allows session injection for tests.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import aiohttp

from config import DOWNLOAD_TIMEOUT_S, REQUEST_RETRY_BACKOFF_S, REQUEST_RETRY_COUNT, USER_AGENT

logger = logging.getLogger(__name__)


class Downloader:
    """Download handler with retry logic and session management.

    Encapsulates file download operations with automatic retries on failure.
    Can accept an external session or create/manage its own.
    """

    def __init__(self, session: aiohttp.ClientSession | None = None):
        """Initialize the downloader.

        Args:
            session: Optional external aiohttp ClientSession. If None, one is created internally.
        """
        self.session = session
        self._owned_session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is not None:
            return self.session
        if self._owned_session is None:
            headers = {"User-Agent": USER_AGENT}
            timeout = aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT_S)
            self._owned_session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self._owned_session

    async def __aenter__(self):
        """Context manager entry; ensures session is initialized."""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Context manager exit; closes owned session if created."""
        await self.close()
        return False

    async def close(self) -> None:
        """Explicitly close the owned session if it was created."""
        if self._owned_session is not None:
            try:
                await self._owned_session.close()
            except Exception:
                pass
            self._owned_session = None

    async def fetch_with_retries(self, url: str) -> Optional[bytes]:
        """Download with retries; returns bytes or None if everything fails."""
        session = await self._get_session()
        attempt = 0
        while attempt < REQUEST_RETRY_COUNT:
            try:
                timeout = aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT_S)
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
        logger.error("Failed to fetch %s after %d attempts", url, REQUEST_RETRY_COUNT)
        return None

    async def download(self, url: str, dest: Path) -> Optional[Path]:
        """Download and save to `dest`, returns path or None if it fails."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = await self.fetch_with_retries(url)
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
