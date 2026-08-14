"""エラーログ本文の伏せ字（FR-031）."""

from __future__ import annotations

from pathlib import Path


def redact_home(text: str, home: Path | None = None) -> str:
    """ユーザーホームパスを `~` に置換する."""
    home_path = (home or Path.home()).resolve()
    home_text = str(home_path)
    redacted = text.replace(home_text, "~")
    home_posix = home_path.as_posix()
    if home_posix != home_text:
        redacted = redacted.replace(home_posix, "~")
    return redacted
