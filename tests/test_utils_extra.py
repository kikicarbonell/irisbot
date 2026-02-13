import importlib
from pathlib import Path

import pytest
from aioresponses import aioresponses


@pytest.mark.asyncio
async def test_download_file_retries_then_success(tmp_path):
    url = "https://example.com/retry.jpg"
    dest = tmp_path / "retry.jpg"
    payload = b"ok"

    # Register two responses: first 500, then 200
    with aioresponses() as m:
        m.get(url, status=500)
        m.get(url, status=200, body=payload)
        from utils import download_file

        result = await download_file(url, dest)
        assert result is not None
        assert dest.exists()
        assert dest.read_bytes() == payload


@pytest.mark.asyncio
async def test_download_file_write_error(tmp_path, monkeypatch):
    url = "https://example.com/writeerr.jpg"
    dest = tmp_path / "writeerr.jpg"
    payload = b"data"

    # Make Path.write_bytes raise only for the temp .part file
    real_write = Path.write_bytes

    def fake_write(self, data):
        if str(self).endswith('.part'):
            raise OSError("disk error")
        return real_write(self, data)

    monkeypatch.setattr(Path, "write_bytes", fake_write)

    with aioresponses() as m:
        m.get(url, status=200, body=payload)
        from utils import download_file

        result = await download_file(url, dest)
        assert result is None
        assert not dest.exists()