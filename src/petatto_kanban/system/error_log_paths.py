"""エラーログのパス・日次ファイル名・保持期限（FR-031）."""

from __future__ import annotations

from datetime import date
from pathlib import Path

APP_DIR_NAME = ".petatto-kanban"
LOGS_DIR_NAME = "logs"
LOG_FILE_PREFIX = "petatto-kanban-"
LOG_FILE_SUFFIX = ".log"
RETENTION_DAYS = 14


def default_logs_dir() -> Path:
    """既定のログディレクトリ."""
    return Path.home() / APP_DIR_NAME / LOGS_DIR_NAME


def log_file_name(day: date) -> str:
    """日次ログファイル名."""
    return f"{LOG_FILE_PREFIX}{day.isoformat()}{LOG_FILE_SUFFIX}"


def log_file_path(logs_dir: Path, day: date | None = None) -> Path:
    """指定日のログファイルパス."""
    return logs_dir / log_file_name(day or date.today())


def parse_log_file_date(name: str) -> date | None:
    """`petatto-kanban-YYYY-MM-DD.log` から日付を取る."""
    if not (name.startswith(LOG_FILE_PREFIX) and name.endswith(LOG_FILE_SUFFIX)):
        return None
    stamp = name[len(LOG_FILE_PREFIX) : -len(LOG_FILE_SUFFIX)]
    try:
        return date.fromisoformat(stamp)
    except ValueError:
        return None


def expired_log_files(
    logs_dir: Path,
    *,
    today: date | None = None,
    retention_days: int = RETENTION_DAYS,
) -> list[Path]:
    """保持期限を過ぎたログファイル."""
    if not logs_dir.is_dir():
        return []
    now = today or date.today()
    expired: list[Path] = []
    for path in logs_dir.glob(f"{LOG_FILE_PREFIX}*{LOG_FILE_SUFFIX}"):
        day = parse_log_file_date(path.name)
        if day is not None and (now - day).days >= retention_days:
            expired.append(path)
    return expired


def purge_old_logs(logs_dir: Path, *, today: date | None = None) -> None:
    """期限切れログを削除する。失敗しても続行する."""
    for path in expired_log_files(logs_dir, today=today):
        try:
            path.unlink()
        except OSError:
            continue
