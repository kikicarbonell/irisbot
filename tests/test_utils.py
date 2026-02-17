import importlib

import pytest
from aioresponses import aioresponses


@pytest.mark.asyncio
async def test_download_file_success(tmp_path):
    # Reload config to ensure defaults
    import config as cfg

    importlib.reload(cfg)

    url = "https://example.com/image.jpg"
    dest = tmp_path / "image.jpg"
    payload = b"binarydata"

    with aioresponses() as m:
        m.get(url, status=200, body=payload)
        from utils import download_file

        result = await download_file(url, dest)
        assert result is not None
        assert dest.exists()
        assert dest.read_bytes() == payload


@pytest.mark.asyncio
async def test_download_file_fail(tmp_path):
    url = "https://example.com/missing.jpg"
    dest = tmp_path / "missing.jpg"
    with aioresponses() as m:
        m.get(url, status=404)
        from utils import download_file

        result = await download_file(url, dest)
        assert result is None
        assert not dest.exists()
