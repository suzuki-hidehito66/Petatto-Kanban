# 10 — トレーサビリティマトリクス

| 項目 | 内容 |
|------|------|
| ステータス | Active |
| 最終更新 | 2026-08-14 |

---

## 使い方

実装・テスト完了時に本表を更新する。  
**verified** = 関連 AC を自動または手動検証済み。

---

## M1 MVP — 機能要件

| FR | US | AC | 実装 | テスト | ステータス |
|----|----|----|------|--------|------------|
| FR-001 | US-001, US-010 | AC-001-01, AC-020-01 | `app.py`, `display/overlay.py` | 手動 | implemented |
| FR-002 | US-001 | AC-002-01, AC-002-02 | `models.py`, `app.py`, `card_renderer.py`, `display/card_layout.py` | `test_create_default_board_is_empty`, `test_resolve_card_frame_size_*` + 手動 | implemented |
| FR-003 | US-002 | AC-003-01, AC-003-02 | `app.py` | 手動 | implemented |
| FR-004 | US-003 | AC-004-01, AC-004-02 | `app.py` | 手動 | implemented |
| FR-005 | US-004 | AC-005-01, AC-005-02, AC-005-03 | `app.py`, `models.py`, `display/settings_actions.py`, `display/settings_dialog_panels.py` | `test_board_clear_cards`, `test_settings_actions.py` + 手動 | implemented |
| FR-007 | US-006 | AC-007-01〜03 | `storage.py`, `app.py` | `test_save_and_load_board`, `test_board_roundtrip_dict`, `test_migrate_legacy_columns_format` | verified |
| FR-010 | US-012 | AC-010-01 | `app.py` | 手動 | implemented |
| FR-020 | US-010 | AC-020-01, AC-020-02 | `display/overlay.py`, `app.py` | 手動 | implemented |
| FR-021 | US-010 | AC-021-01 | `display/monitors.py`, `display/settings.py`, `app.py` | `test_display_settings.py` | implemented |
| FR-023 | US-011 | AC-023-01, AC-023-02 | `app.py`, `display/settings.py`, `display/settings_actions.py`, `display/settings_dialog.py` | `test_display_settings.py`, `test_settings_dialog.py`, `test_settings_actions.py` + 手動 | implemented |
| FR-024 | US-013 | AC-024-01 | `display/settings.py`, `app.py` | `test_display_settings.py` | implemented |
| FR-025 | US-014 | AC-025-01, AC-025-02, AC-025-03 | `app.py`, `progress.py` | `test_progress.py`, `test_board_roundtrip_dict_with_progress` | implemented |
| FR-014 | US-015 | AC-014-01, AC-014-02, AC-014-03, AC-014-04 | `app.py`, `due_date.py`, `due_date_picker.py`, `card_ui.py` | `test_due_date.py`, `test_board_roundtrip_dict_with_due_date` | implemented |
| FR-006 | US-005 | AC-006-01 | （M2） | — | deferred |
| FR-008 | US-006 | AC-008-01 | （M2） | — | deferred |
| FR-009 | US-006 | AC-009-01 | （M2） | — | deferred |
| FR-018 | US-008 | AC-018-01 | （M2） | 手動 | deferred |
| FR-019 | US-009 | AC-019-01, AC-019-02 | `display/desktop.py`, `display/menu_panel_host.py`, `display/desktop_board_controller.py`, `display/foreground.py`, `display/modes.py` | `test_display_modes.py` + 手動 | implemented |
| FR-022 | US-008, US-009, US-010 | AC-022-01, AC-022-02 | `display/settings_dialog.py`, `display/settings_dialog_panels.py`, `display/modes.py`, `app.py` | `test_display_modes.py`, `test_settings_dialog.py` + 手動 | implemented |
| FR-026 | US-016 | AC-026-01〜04 | `display/ui_scale.py`, `display/ui_scale_labels.py`, `display/card_layout.py`, `display/ui_metrics.py`, `display/ui_chrome.py`, `card_renderer.py`, `settings.py`, `app.py`, `menu_panel_layout.py`, `menu_panel.py`, `due_date_picker.py` | `test_ui_scale.py`, `test_card_layout.py`, `test_ui_scale_labels.py`, `test_settings_dialog.py`, `test_display_settings.py` + 手動 | implemented |
| FR-027 | US-017 | AC-027-01, AC-027-02, AC-027-03 | `display/ui_font.py`, `display/ui_font_labels.py`, `display/ui_metrics.py`, `display/card_layout.py`, `settings.py`, `app.py`, `display/ui_chrome.py`, `card_renderer.py` | `test_ui_font.py`, `test_settings_dialog.py`, `test_display_settings.py`, `test_settings_actions.py` + 手動 | implemented |
| FR-028 | US-018 | AC-028-01, AC-028-02, AC-028-03 | `display/ui_theme.py`, `display/ui_theme_labels.py`, `settings.py`, `app.py`, `display/ui_chrome.py`, `card_renderer.py`, `menu_panel.py`, `due_date_picker.py` | `test_ui_theme.py`, `test_settings_dialog.py`, `test_display_settings.py`, `test_settings_actions.py` + 手動 | implemented |
| FR-029 | US-019 | AC-029-01, AC-029-02, AC-029-03, AC-029-05, AC-029-06（AC-029-04 cancelled） | `system/auto_start.py`, `system/launch_command.py`, `display/settings.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `app.py` | `test_auto_start.py`, `test_launch_command.py`, `test_display_settings.py`, `test_settings_dialog.py`, `test_settings_actions.py` + 手動 | implemented |
| FR-030 | US-020 | AC-030-01〜05 | `system/shortcut.py`, `system/hotkey.py`, `system/hotkey_pump.py`, `display/settings.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `app.py` | `test_shortcut.py`, `test_hotkey.py`, `test_display_settings.py`, `test_settings_dialog.py`, `test_settings_actions.py` + 手動 | implemented |

---

## M1 MVP — 非機能要件

| NFR | AC | 実装 / 検証 | ステータス |
|-----|----|-------------|------------|
| NFR-001 | AC-NFR-001-01 | 手動（未実施） | specified |
| NFR-002 | — | `app.py` 定数 | implemented |
| NFR-003 | AC-007-01, AC-007-02 | `tests/test_models_and_storage.py` | verified |
| NFR-004 | — | `petatto-kanban.spec`, CI | implemented |
| NFR-005 | — | `pyproject.toml` | verified |
| NFR-006 | — | `ruff check` | verified |
| NFR-007 | — | `pytest` | verified |
| NFR-008 | AC-NFR-008-01, AC-NFR-008-02 | `pyproject.toml`（依存空）, アーキテクチャ | verified / specified |
| NFR-011 | AC-NFR-011-01 | CI `windows-latest`, ドキュメント | specified |

---

## M1 MVP — データ / UI 契約

| 契約 | 関連 FR | 実装 | テスト | ステータス |
|------|---------|------|--------|------------|
| DC-001 | FR-007 | `storage.py` | `test_*` | verified |
| DC-002 | FR-002, FR-007 | `models.py` | `test_create_default_board_is_empty` | verified |
| DC-003 | FR-021, FR-024, FR-026, FR-027, FR-028, FR-029, FR-030 | `display/settings.py` | `test_display_settings.py` | implemented |
| UC-001 | FR-001, FR-019, FR-020 | `app.py`, `display/modes.py`, `display/overlay.py`, `display/desktop.py` | 手動 | implemented |
| UC-002 | FR-003, FR-019, FR-023 | `menu_panel.py`, `menu_panel_layout.py`, `display/menu_panel_host.py`, `display/desktop_board_controller.py`, `app.py` | `test_menu_panel.py`, `test_display_modes.py` + 手動 | implemented |
| UC-006 | FR-005, FR-019, FR-020, FR-021, FR-022, FR-023, FR-024, FR-026, FR-027, FR-028, FR-029, FR-030 | `display/settings_dialog.py`, `settings_dialog_tabs.py`, `settings_dialog_labels.py`, `settings_dialog_panels.py`, `settings_actions.py`, `display/ui_scale.py`, `display/ui_font.py`, `display/ui_theme.py`, `system/auto_start.py`, `system/launch_command.py`, `system/shortcut.py`, `system/hotkey.py`, `system/hotkey_pump.py`, `mode_labels.py`, `app.py` | `test_display_modes.py`, `test_settings_dialog.py`, `test_settings_actions.py`, `test_auto_start.py`, `test_launch_command.py`, `test_shortcut.py`, `test_hotkey.py`, `test_ui_scale.py`, `test_ui_font.py`, `test_ui_theme.py` + 手動 | implemented |
| UC-012 | FR-030, FR-003 | `system/shortcut.py`, `system/hotkey.py`, `system/hotkey_pump.py`, `app.py` | `test_shortcut.py`, `test_hotkey.py` + 手動 | implemented |
| UC-011 | FR-028 | `display/ui_theme.py`, `display/ui_theme_labels.py`, `card_renderer.py`, `menu_panel.py`, `due_date_picker.py`, `display/ui_chrome.py`, `app.py` | `test_ui_theme.py` + 手動 | implemented |
| UC-009 | FR-026, FR-027 | `display/ui_scale.py`, `display/card_layout.py`, `display/ui_font.py`, `display/ui_metrics.py`, `display/ui_chrome.py`, `card_renderer.py`, `app.py`, `menu_panel_layout.py`, `menu_panel.py`, `due_date_picker.py` | `test_ui_scale.py`, `test_card_layout.py`, `test_ui_font.py` + 手動 | implemented |
| UC-010 | FR-027 | `display/ui_font.py`, `display/ui_font_labels.py`, `display/ui_metrics.py`, `app.py`, `card_renderer.py`, `display/ui_chrome.py`, `menu_panel.py`, `due_date_picker.py` | `test_ui_font.py` + 手動 | implemented |
| UC-003 | FR-002, FR-003〜005, FR-010, FR-014, FR-025, FR-026, FR-028 | `app.py`, `card_renderer.py`, `card_ui.py`, `display/card_layout.py`, `display/ui_metrics.py` | `test_card_layout.py` + 手動 | implemented |
| UC-004 | FR-003, FR-030 | `app.py`, `menu_panel.py`, `menu_panel_layout.py`, `new_card_placement.py` | `test_new_card_placement.py`, `test_menu_panel.py` + 手動 | implemented |
| UC-005 | FR-004 | `app.py` | 手動 | implemented |
| UC-008 | FR-014 | `app.py`, `due_date_picker.py`, `card_ui.py` | 手動 | implemented |
| UC-DM-002 | FR-019 | `display/desktop.py`, `display/menu_panel_host.py`, `display/desktop_board_controller.py`, `display/foreground.py`, `display/modes.py`, `app.py` | `test_display_modes.py` + 手動 | implemented |
| UC-DM-003 | FR-020 | `display/overlay.py`, `display/modes.py`, `app.py` | 手動 | implemented |
| UC-DM-001 | FR-018 | （M2） | 手動 | deferred |
| UC-DM-004 | FR-022 | `app.py`, `display/modes.py` | `test_display_modes.py` + 手動 | implemented |

---

## M1 完了判定

| 条件 | 状態 |
|------|------|
| Must の FR が `implemented` 以上 | ✅（自動テスト対象は verified） |
| Must の NFR が `verified` | ⚠️ NFR-001 の手動検証が未実施 |
| Must の US が `implemented` 以上 | ⚠️ 手動検証待ち |
| DC-001 テストパス | ✅ |
| CI（pytest + ruff + exe ビルド） | ✅（Windows CI） |

**M1 残タスク**
- [ ] オーバーレイ UI の Windows 手動検証（透過・最前面・ドラッグ・右クリック削除）
- [ ] FR-003〜005, FR-010, FR-014, FR-025, FR-020, FR-023, FR-024 の手動検証 → `verified` へ更新
- [ ] NFR-001 手動パフォーマンス検証

---

## 更新ルール

1. 新 FR 追加時: 03-functional-requirements.md → 06-acceptance-criteria.md → 本表の順で更新
2. 実装完了: 「実装」列を記入しステータスを `implemented`
3. テスト追加: 「テスト」列を記入
4. 検証完了: ステータスを `verified`
