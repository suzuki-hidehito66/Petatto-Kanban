"""ローカルエラーログの初期化と例外フック（FR-031）."""

from __future__ import annotations

import logging
import platform
import sys
import threading
from contextlib import suppress
from datetime import date, datetime
from pathlib import Path
from typing import Any, TextIO

from petatto_kanban import __version__
from petatto_kanban.system.error_log_paths import (
    RETENTION_DAYS,
    default_logs_dir,
    expired_log_files,
    log_file_name,
    log_file_path,
    parse_log_file_date,
    purge_old_logs,
)
from petatto_kanban.system.error_log_redact import redact_home

LOGGER_NAME = "petatto_kanban"

_handler: logging.Handler | None = None

__all__ = [
    "DailyFileHandler",
    "RETENTION_DAYS",
    "active_handler",
    "default_logs_dir",
    "expired_log_files",
    "get_logger",
    "install_error_logging",
    "log_file_name",
    "log_tk_callback_exception",
    "log_uncaught_exception",
    "parse_log_file_date",
    "redact_home",
]


def get_logger() -> logging.Logger:
    """アプリ用ロガー."""
    return logging.getLogger(LOGGER_NAME)


def active_handler() -> logging.Handler | None:
    """現在のファイル（または Null）ハンドラ."""
    return _handler


def install_error_logging(*, logs_dir: Path | None = None) -> Path:
    """エラーログを初期化する。失敗しても例外は出さない."""
    directory = logs_dir or default_logs_dir()
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        _install_logger(handler=logging.NullHandler())
        _install_exception_hooks()
        return directory
    purge_old_logs(directory)
    handler = DailyFileHandler(directory)
    handler.setLevel(logging.ERROR)
    handler.setFormatter(_ErrorLogFormatter())
    handler.addFilter(_ContextFilter())
    _install_logger(handler=handler)
    _install_exception_hooks()
    return directory


def log_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: object,
    *,
    where: str = "Uncaught exception",
) -> None:
    """未捕捉例外を ERROR で記録する."""
    get_logger().error(where, exc_info=(exc_type, exc_value, exc_traceback))


def log_tk_callback_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: object,
) -> None:
    """tkinter `report_callback_exception` 用."""
    log_uncaught_exception(
        exc_type,
        exc_value,
        exc_traceback,
        where="Tk callback exception",
    )


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
    log_uncaught_exception(exc_type, exc_value, exc_traceback)


def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
    name = args.thread.name if args.thread is not None else "unknown"
    log_uncaught_exception(
        args.exc_type,
        args.exc_value,
        args.exc_traceback,
        where=f"Uncaught exception in thread {name}",
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


class DailyFileHandler(logging.Handler):
    """日付ごとのファイルへ追記する。書き込み失敗では例外を出さない."""

    def __init__(self, logs_dir: Path) -> None:
        super().__init__()
        self.logs_dir = logs_dir
        self._stream: TextIO | None = None
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
        path = log_file_path(self.logs_dir, day)
        self._stream = path.open("a", encoding="utf-8")
        self._current_day = day
        return self._stream
