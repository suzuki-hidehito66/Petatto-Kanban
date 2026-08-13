"""UI フォントプリセット（FR-027 / UC-010）."""

from __future__ import annotations

from enum import StrEnum

DEFAULT_FONT_FAMILY = "Segoe UI"


class UiFont(StrEnum):
    """UI フォントプリセット."""

    SEGOE_UI = "segoe_ui"
    MEIRYO = "meiryo"
    YU_GOTHIC_UI = "yu_gothic_ui"
    MS_GOTHIC = "ms_gothic"


UI_FONT_TKINTER_FAMILIES: dict[UiFont, str] = {
    UiFont.SEGOE_UI: "Segoe UI",
    UiFont.MEIRYO: "Meiryo",
    UiFont.YU_GOTHIC_UI: "Yu Gothic UI",
    UiFont.MS_GOTHIC: "MS Gothic",
}


def parse_ui_font(value: str | None) -> UiFont:
    """settings.json の ui_font をパース。不正値は segoe_ui。"""
    if value is None:
        return UiFont.SEGOE_UI
    try:
        return UiFont(value)
    except ValueError:
        return UiFont.SEGOE_UI


def tkinter_family_name(ui_font: UiFont) -> str:
    """プリセットに対応する tkinter フォントファミリー名。"""
    return UI_FONT_TKINTER_FAMILIES.get(ui_font, DEFAULT_FONT_FAMILY)


def resolve_font_family(
    requested: str,
    *,
    available_families: frozenset[str] | None = None,
) -> str:
    """OS 上で利用可能なファミリー名を返す。不可なら Segoe UI へフォールバック。"""
    families = available_families if available_families is not None else _load_font_families()
    if families and requested in families:
        return requested
    if families and DEFAULT_FONT_FAMILY in families:
        return DEFAULT_FONT_FAMILY
    return requested


def _load_font_families() -> frozenset[str]:
    try:
        import tkinter.font as tkfont

        return frozenset(tkfont.families())
    except ImportError:
        return frozenset()
    except Exception:
        return frozenset()
