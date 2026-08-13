"""アプリリリースバージョンの同期検証（CI / リリース用）."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import petatto_kanban

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PLAN = ROOT / "docs" / "spec" / "11-release-plan.md"
PYPROJECT = ROOT / "pyproject.toml"

APP_VERSION_PATTERN = re.compile(
    r"\|\s*バージョン\s*\|\s*`(\d+\.\d+\.\d+)`\s*\|",
)


def _pyproject_version() -> str:
    with PYPROJECT.open("rb") as file:
        data = tomllib.load(file)
    return str(data["project"]["version"])


def _release_plan_version() -> str:
    text = RELEASE_PLAN.read_text(encoding="utf-8")
    match = APP_VERSION_PATTERN.search(text)
    if match is None:
        raise AssertionError(
            "docs/spec/11-release-plan.md に "
            "| バージョン | `x.y.z` | 行（アプリリリースバージョン）が必要です"
        )
    return match.group(1)


def test_app_version_is_synchronized() -> None:
    expected = _pyproject_version()
    assert petatto_kanban.__version__ == expected
    assert _release_plan_version() == expected
