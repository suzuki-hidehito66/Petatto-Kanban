# 10 — トレーサビリティマトリクス

| 項目 | 内容 |
|------|------|
| ステータス | Active |
| 最終更新 | 2026-08-12 |

---

## 使い方

実装・テスト完了時に本表を更新する。  
**verified** = 関連 AC を自動または手動検証済み。

---

## M1 MVP — 機能要件

| FR | US | AC | 実装 | テスト | ステータス |
|----|----|----|------|--------|------------|
| FR-001 | US-001 | AC-001-01 | `app.py` | 手動 | verified |
| FR-002 | US-001 | AC-002-01 | `models.py`, `app.py` | `test_create_default_board_has_three_columns` | verified |
| FR-003 | US-002 | AC-003-01, AC-003-02 | `app.py` | 手動 | implemented |
| FR-004 | US-003 | AC-004-01 | `app.py` | 手動 | implemented |
| FR-005 | US-004 | AC-005-01 | `app.py` | 手動 | implemented |
| FR-006 | US-005 | AC-006-01 | `app.py` | 手動 | implemented |
| FR-007 | US-006 | AC-007-01〜03 | `storage.py`, `app.py` | `test_save_and_load_board`, `test_board_roundtrip_dict`, `test_load_missing_file_returns_default` | verified |
| FR-008 | US-006 | AC-008-01 | `app.py` | 手動 | implemented |
| FR-009 | US-006 | AC-009-01 | `app.py` | 手動 | implemented |
| FR-018 | US-008 | AC-018-01 | `app.py` | 手動 | verified |
| FR-019 | US-009 | AC-019-01, AC-019-02 | （未実装） | 手動 | specified |
| FR-020 | US-010 | AC-020-01, AC-020-02 | （未実装） | 手動 | specified |
| FR-021 | US-009, US-010 | AC-021-01 | （未実装） | 手動 | specified |
| FR-022 | US-008〜010 | AC-022-01 | （未実装） | 手動 | specified |

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

---

## M1 MVP — データ / UI 契約

| 契約 | 関連 FR | 実装 | テスト | ステータス |
|------|---------|------|--------|------------|
| DC-001 | FR-007 | `storage.py` | `test_*` | verified |
| DC-002 | FR-002, FR-007 | `models.py` | `test_create_default_board_has_three_columns` | verified |
| UC-001 | FR-001, FR-002 | `app.py` | 手動 | verified |
| UC-002 | FR-008, FR-009 | `app.py` | 手動 | implemented |
| UC-003 | FR-002 | `app.py` | 手動 | verified |
| UC-004 | FR-003〜006 | `app.py` | 手動 | implemented |
| UC-005 | FR-003 | `app.py` | 手動 | implemented |
| UC-006 | FR-004 | `app.py` | 手動 | implemented |
| UC-DM-001 | FR-018 | `app.py` | 手動 | verified |
| UC-DM-002 | FR-019 | （未実装） | 手動 | specified |
| UC-DM-003 | FR-020 | （未実装） | 手動 | specified |
| UC-DM-004 | FR-022 | （未実装） | 手動 | specified |

---

## M1 完了判定

| 条件 | 状態 |
|------|------|
| Must の FR が `implemented` 以上 | ✅（FR-003〜009 は implemented、FR-001/002/007 は verified） |
| Must の NFR が `verified` | ⚠️ NFR-001 の手動検証が未実施 |
| Must の US が `implemented` 以上 | ✅ |
| DC-001 テストパス | ✅ |
| CI（pytest + ruff + exe ビルド） | ✅（Windows CI） |

**M1 残タスク**
- [ ] FR-003〜006, FR-008, FR-009 の手動検証完了 → `verified` へ更新
- [ ] NFR-001 手動パフォーマンス検証

---

## 更新ルール

1. 新 FR 追加時: 03-functional-requirements.md → 06-acceptance-criteria.md → 本表の順で更新
2. 実装完了: 「実装」列を記入しステータスを `implemented`
3. テスト追加: 「テスト」列を記入
4. 検証完了: ステータスを `verified`
