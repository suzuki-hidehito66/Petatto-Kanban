"""エラーログ（FR-031）のテスト."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from petatto_kanban import __version__
from petatto_kanban.system import error_log
from petatto_kanban.system.error_log import (
    RETENTION_DAYS,
    expired_log_files,
    get_logger,
    install_error_logging,
    log_file_name,
    log_tk_callback_exception,
    parse_log_file_date,
    redact_home,
)


def test_install_creates_logs_directory(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    assert not logs_dir.exists()
    result = install_error_logging(logs_dir=logs_dir)
    assert result == logs_dir
    assert logs_dir.is_dir()


def test_uncaught_exception_is_written_to_daily_file(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    install_error_logging(logs_dir=logs_dir)
    try:
        raise RuntimeError("probe-error")
    except RuntimeError:
        error_log._sys_excepthook(*sys.exc_info())

    log_path = logs_dir / log_file_name(date.today())
    text = log_path.read_text(encoding="utf-8")
    assert "ERROR" in text
    assert "RuntimeError" in text
    assert "probe-error" in text
    assert "app=" + __version__ in text
    assert "py=" in text
    assert "os=" in text
    assert "新しいタスク" not in text


def test_tk_callback_exception_is_written(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    install_error_logging(logs_dir=logs_dir)
    try:
        raise ValueError("tk-probe")
    except ValueError:
        log_tk_callback_exception(*sys.exc_info())

    text = (logs_dir / log_file_name(date.today())).read_text(encoding="utf-8")
    assert "Tk callback exception" in text
    assert "ValueError" in text
    assert "tk-probe" in text


def test_redact_home_replaces_user_path() -> None:
    home = Path("/home/alice")
    text = redact_home(f"fail at {home / 'secret.txt'}", home=home)
    assert str(home) not in text
    assert "~/secret.txt" in text


def test_home_path_in_exception_is_redacted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "userhome"
    home.mkdir()
    monkeypatch.setattr(error_log.Path, "home", staticmethod(lambda: home))
    logs_dir = tmp_path / "logs"
    install_error_logging(logs_dir=logs_dir)
    try:
        raise RuntimeError(str(home / "board.json"))
    except RuntimeError:
        error_log._sys_excepthook(*sys.exc_info())

    text = (logs_dir / log_file_name(date.today())).read_text(encoding="utf-8")
    assert str(home) not in text
    assert "~/board.json" in text


def test_write_failure_does_not_raise(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    install_error_logging(logs_dir=logs_dir)
    handler = error_log._handler
    assert isinstance(handler, error_log._DailyFileHandler)
    handler._current_day = None
    handler._stream = None
    handler._logs_dir = tmp_path / "missing" / "nested"
    get_logger().error("should-not-raise")


def test_install_does_not_raise_when_logs_dir_is_a_file(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    logs_dir.write_text("not-a-directory", encoding="utf-8")
    install_error_logging(logs_dir=logs_dir)
    get_logger().error("still-ok")


def test_expired_log_files_are_removed_on_install(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    today = date.today()
    keep = logs_dir / log_file_name(today - timedelta(days=RETENTION_DAYS - 1))
    drop = logs_dir / log_file_name(today - timedelta(days=RETENTION_DAYS))
    keep.write_text("keep", encoding="utf-8")
    drop.write_text("drop", encoding="utf-8")
    install_error_logging(logs_dir=logs_dir)
    assert keep.exists()
    assert not drop.exists()


def test_parse_log_file_date() -> None:
    assert parse_log_file_date("petatto-kanban-2026-08-14.log") == date(2026, 8, 14)
    assert parse_log_file_date("other.log") is None


def test_expired_log_files_helper(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    today = date(2026, 8, 14)
    old = logs_dir / log_file_name(date(2026, 7, 31))
    old.write_text("x", encoding="utf-8")
    expired = expired_log_files(logs_dir, today=today, retention_days=14)
    assert expired == [old]
