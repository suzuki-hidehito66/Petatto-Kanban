"""Tests for scripts/prepare_exe_build.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from prepare_exe_build import _remove_or_rename, is_process_running


def test_is_process_running_non_windows() -> None:
    assert is_process_running("Petatto-Kanban.exe") is False


def test_remove_or_rename_deletes_file(tmp_path: Path) -> None:
    target = tmp_path / "Petatto-Kanban.exe"
    target.write_text("dummy", encoding="utf-8")
    assert _remove_or_rename(target) is True
    assert not target.exists()
