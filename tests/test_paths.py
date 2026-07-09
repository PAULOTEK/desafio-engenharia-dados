from pathlib import Path

from src.utils.paths import ensure_path


def test_ensure_path_creates_directory(tmp_path):
    target = tmp_path / "nested" / "dir"
    result = ensure_path(str(target))

    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()


def test_ensure_path_is_idempotent(tmp_path):
    target = tmp_path / "existing"
    ensure_path(str(target))
    # Calling again on an existing directory must not raise.
    result = ensure_path(str(target))
    assert result.exists()
