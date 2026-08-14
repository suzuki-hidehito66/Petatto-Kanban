"""エラーログ本文の伏せ字（FR-031）."""

from __future__ import annotations

from pathlib import Path


def redact_home(text: str, home: Path | None = None) -> str:
    """ユーザーホームパスを `~` に置換する.

    Windows では `Path` の文字列が `\\` 区切り、トレースバックが `/` 区切りの
    ことがあるので、両方を置換する。置換後の残りは `~/...` に揃える。
    """
    redacted = text
    for variant in _home_text_variants(home or Path.home()):
        redacted = redacted.replace(variant, "~")
    return redacted.replace("~\\", "~/")


def _home_text_variants(home: Path) -> tuple[str, ...]:
    """ログに出うるホームパス表記（長い順。短い誤置換を避ける）."""
    variants: set[str] = set()
    for path in (home, home.expanduser(), home.resolve()):
        native = str(path)
        posix = path.as_posix()
        variants.update(
            (
                native,
                posix,
                native.replace("/", "\\"),
                posix.replace("/", "\\"),
            )
        )
    return tuple(
        variant
        for variant in sorted(variants, key=len, reverse=True)
        if len(variant) > 1
    )
