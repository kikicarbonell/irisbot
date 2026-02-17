"""Unit tests for downloader.py"""

import pytest
from aioresponses import aioresponses


@pytest.mark.asyncio
async def test_downloader_success(tmp_path):
    from downloader import Downloader

    url = "https://example.com/file.bin"
    dest = tmp_path / "file.bin"
    payload = b"content"

    with aioresponses() as m:
        m.get(url, status=200, body=payload)
        dl = Downloader()
        result = await dl.download(url, dest)

        assert result is not None
        assert dest.exists()
        assert dest.read_bytes() == payload


@pytest.mark.asyncio
async def test_downloader_retries_then_fails(tmp_path):
    from downloader import Downloader

    url = "https://example.com/nope.bin"
    dest = tmp_path / "nope.bin"

    with aioresponses() as m:
        # All attempts fail
        m.get(url, status=500)
        m.get(url, status=500)
        m.get(url, status=500)
        dl = Downloader()
        result = await dl.download(url, dest)

        assert result is None
        assert not dest.exists()


@pytest.mark.asyncio
async def test_downloader_fetch_with_retries_success(tmp_path):
    from downloader import Downloader

    url = "https://example.com/retry.bin"
    payload = b"ok"

    with aioresponses() as m:
        # Fail once, then succeed
        m.get(url, status=500)
        m.get(url, status=200, body=payload)
        dl = Downloader()
        result = await dl.fetch_with_retries(url)

        assert result == payload


@pytest.mark.asyncio
async def test_downloader_write_error_closes_temp(tmp_path, monkeypatch):
    from pathlib import Path

    from downloader import Downloader

    url = "https://example.com/file.bin"
    dest = tmp_path / "file.bin"
    payload = b"data"

    real_write = Path.write_bytes

    def fake_write(self, data):
        if str(self).endswith(".part"):
            raise OSError("mock write error")
        return real_write(self, data)

    monkeypatch.setattr(Path, "write_bytes", fake_write)

    with aioresponses() as m:
        m.get(url, status=200, body=payload)
        dl = Downloader()
        result = await dl.download(url, dest)

        assert result is None
        assert not dest.exists()


@pytest.mark.asyncio
async def test_downloader_context_manager():
    """Test that Downloader works as async context manager and closes owned session on exit."""
    from downloader import Downloader

    dl = Downloader()
    # Before context manager, no owned session
    assert dl._owned_session is None

    # Use as context manager
    async with dl as dl_ctx:
        assert dl_ctx is dl
        # Context manager enters and initializes session
        await dl._get_session()
        assert dl._owned_session is not None

    # After exit, owned session should be cleared
    assert dl._owned_session is None
