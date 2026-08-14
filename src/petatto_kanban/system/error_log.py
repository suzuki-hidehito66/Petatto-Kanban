"""ローカルエラーログ（FR-031）."""

from __future__ import annotations

import logging
import platform
import sys
import threading
from contextlib import suppress
from datetime import date, datetime
from pathlib import Path
from typing import Any

from petatto_kanban import __version__

APP_DIR_NAME = ".petatto-kanban"
LOGS_DIR_NAME = "logs"
LOG_FILE_PREFIX = "petatto-kanban-"
LOG_FILE_SUFFIX = ".log"
RETENTION_DAYS = 14
LOGGER_NAME = "petatto_kanban"

_handler: logging.Handler | None = None


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
    prefix = LOG_FILE_PREFIX
    suffix = LOG_FILE_SUFFIX
    if not (name.startswith(prefix) and name.endswith(suffix)):
        return None
    stamp = name[len(prefix) : -len(suffix)]
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


def redact_home(text: str, home: Path | None = None) -> str:
    """ユーザーホームパスを `~` に置換する."""
    home_path = (home or Path.home()).resolve()
    home_text = str(home_path)
    redacted = text.replace(home_text, "~")
    home_posix = home_path.as_posix()
    if home_posix != home_text:
        redacted = redacted.replace(home_posix, "~")
    return redacted


def get_logger() -> logging.Logger:
    """アプリ用ロガー."""
    return logging.getLogger(LOGGER_NAME)


def install_error_logging(*, logs_dir: Path | None = None) -> Path:
    """エラーログを初期化する。失敗しても例外は出さない."""
    directory = logs_dir or default_logs_dir()
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        _install_logger(handler=logging.NullHandler())
        _install_exception_hooks()
        return directory
    _purge_old_logs(directory)
    handler = _DailyFileHandler(directory)
    handler.setLevel(logging.ERROR)
    handler.setFormatter(_ErrorLogFormatter())
    handler.addFilter(_ContextFilter())
    _install_logger(handler=handler)
    _install_exception_hooks()
    return directory


def log_tk_callback_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: object,
) -> None:
    """tkinter `report_callback_exception` 用."""
    get_logger().error(
        "Tk callback exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def _purge_old_logs(logs_dir: Path) -> None:
    for path in expired_log_files(logs_dir):
        try:
            path.unlink()
        except OSError:
            continue


def _install_logger(*, handler: logging.Handler) -> None:
    global _handler
    logger = get_logger()
    logger.setLevel(logging.ERROR)
    logger.propagate = False
    if _handler is not None:
        logger.removeHandler(_handler)
        with suppress(OSError):
            _handler.close()
    logger.addHandler(handler)
    _handler = handler


def _install_exception_hooks() -> None:
    sys.excepthook = _sys_excepthook
    threading.excepthook = _thread_excepthook


def _sys_excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: object,
) -> None:
    get_logger().error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
    name = args.thread.name if args.thread is not None else "unknown"
    get_logger().error(
        "Uncaught exception in thread %s",
        name,
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


class _ContextFilter(logging.Filter):
    """レコードにアプリ・Python・OS 情報を付ける."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.app_version = __version__
        record.python_version = sys.version.split()[0]
        record.os_name = platform.platform()
        return True


class _ErrorLogFormatter(logging.Formatter):
    """ISO 8601・コンテキスト付き。ホームパスは伏せる."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        del datefmt
        return datetime.fromtimestamp(record.created).astimezone().isoformat(timespec="seconds")

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        timestamp = self.formatTime(record)
        app_version = getattr(record, "app_version", __version__)
        python_version = getattr(record, "python_version", sys.version.split()[0])
        os_name = getattr(record, "os_name", platform.platform())
        line = (
            f"{timestamp} {record.levelname} {record.name} "
            f"app={app_version} py={python_version} os={os_name} {record.message}"
        )
        if record.exc_info:
            line = f"{line}\n{self.formatException(record.exc_info)}"
        return redact_home(line)


class _DailyFileHandler(logging.Handler):
    """日付ごとのファイルへ追記する。書き込み失敗は握りつぶさないが例外は出さない."""

    def __init__(self, logs_dir: Path) -> None:
        super().__init__()
        self._logs_dir = logs_dir
        self._stream: Any = None
        self._current_day: date | None = None

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            stream = self._stream_for(date.today())
            stream.write(message + "\n")
            stream.flush()
        except OSError:
            return

    def close(self) -> None:
        with suppress(OSError):
            if self._stream is not None:
                self._stream.close()
        self._stream = None
        self._current_day = None
        super().close()

    def _stream_for(self, day: date) -> Any:
        if self._stream is not None and self._current_day == day:
            return self._stream
        if self._stream is not None:
            with suppress(OSError):
                self._stream.close()
            self._stream = None
        path = log_file_path(self._logs_dir, day)
        self._stream = path.open("a", encoding="utf-8")
        self._current_day = day
        return self._stream
