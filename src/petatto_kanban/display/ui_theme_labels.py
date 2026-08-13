"""UI カラーテーマの UI ラベル（tkinter 非依存）."""

from __future__ import annotations

from petatto_kanban.display.ui_theme import UiTheme

UI_THEME_LABELS: dict[UiTheme, str] = {
    UiTheme.DEFAULT: "Default",
    UiTheme.DARK: "ダーク",
    UiTheme.SANDY: "サンディ",
    UiTheme.FOREST: "フォレスト",
    UiTheme.FANCY: "ファンシー",
    UiTheme.OCEAN: "オーシャン",
    UiTheme.SUNSET: "サンセット",
    UiTheme.SLATE: "スレート",
    UiTheme.ROSE: "ローズ",
    UiTheme.MIDNIGHT: "ミッドナイト",
}

SELECTABLE_UI_THEMES: tuple[UiTheme, ...] = (
    UiTheme.DEFAULT,
    UiTheme.DARK,
    UiTheme.SANDY,
    UiTheme.FOREST,
    UiTheme.FANCY,
    UiTheme.OCEAN,
    UiTheme.SUNSET,
    UiTheme.SLATE,
    UiTheme.ROSE,
    UiTheme.MIDNIGHT,
)


def ui_theme_label(ui_theme: UiTheme) -> str:
    return UI_THEME_LABELS.get(ui_theme, UI_THEME_LABELS[UiTheme.DEFAULT])


def ui_theme_from_label(label: str, default: UiTheme) -> UiTheme:
    for theme, theme_label in UI_THEME_LABELS.items():
        if theme_label == label:
            return theme
    return default


def selectable_ui_theme_labels() -> list[str]:
    return [UI_THEME_LABELS[theme] for theme in SELECTABLE_UI_THEMES]
