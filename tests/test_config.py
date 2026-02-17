import importlib


def test_ensure_dirs_creates_paths(tmp_path, monkeypatch):
    # Set env vars before importing config so constants use tmp_path
    monkeypatch.setenv("PROJECT_NAME", "testproj")
    monkeypatch.setenv("BASE_DIR", str(tmp_path))

    # Reload config module to pick up env changes
    import config as cfg

    importlib.reload(cfg)

    # Ensure dirs doesn't raise and creates the data dir
    cfg.ensure_dirs()
    data_dir = cfg.DATA_DIR
    assert data_dir.exists()
    assert data_dir.is_dir()
