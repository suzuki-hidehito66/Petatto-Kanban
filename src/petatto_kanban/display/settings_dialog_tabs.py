"""設定ダイアログのタブラベルとタブ別項目定義."""

from __future__ import annotations

SETTINGS_TAB_DISPLAY = "表示"
SETTINGS_TAB_THEME = "テーマ"
SETTINGS_TAB_SYSTEM = "システム"

# 表示タブ: FR-019, FR-020, FR-021, FR-022, FR-026, FR-027
DISPLAY_TAB_FIELDS = ("mode", "monitor_index", "ui_size", "ui_font")

# テーマタブ: FR-028
THEME_TAB_FIELDS = ("ui_theme",)

# システムタブ: FR-024, FR-023, FR-029, FR-005（全カード削除ボタン）
SYSTEM_TAB_FIELDS = ("confirm_delete", "confirm_exit", "launch_at_login")
SYSTEM_TAB_ACTIONS = ("delete_all_cards",)
