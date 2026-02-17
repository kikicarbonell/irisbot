import pytest
from aioresponses import aioresponses


@pytest.mark.asyncio
async def test_fetch_with_retries_all_fail(tmp_path):
    # Ensure that when all attempts fail, helper returns None and no file created
    url = "https://example.com/always500.jpg"
    dest = tmp_path / "always500.jpg"

    with aioresponses() as m:
        # three failures according to default REQUEST_RETRY_COUNT=3
        m.get(url, status=500)
        m.get(url, status=500)
        m.get(url, status=500)
        from utils import download_file

        res = await download_file(url, dest)
        assert res is None
        assert not dest.exists()
