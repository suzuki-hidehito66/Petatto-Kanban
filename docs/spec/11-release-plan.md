# 11 — リリース計画

| 項目 | 内容 |
|------|------|
| ステータス | Active |

---

## アプリリリースバージョン

GitHub Releases のタグ（`v0.1.0` 形式）は **`pyproject.toml` の `[project].version`** を正とする。以下 3 箇所を **常に同一値** に保ち、CI（`tests/test_release_version.py`）で検証する。

| 項目 | 値 |
|------|-----|
| バージョン | `0.1.7` |
| 同期先 | `pyproject.toml` `[project].version`、`src/petatto_kanban/__init__.py` `__version__` |

**main へマージ（PR マージ）時**: `build-windows.yml` が exe をビルドし、未使用の `v{バージョン}` タグで [GitHub Release](https://github.com/suzuki-hidehito66/Petatto-Kanban/releases) を作成する。同じバージョンで再マージする場合は **リリース前にバージョンをインクリメント** すること（タグ重複で CI が失敗する）。

`main` への取り込みは **`test` からの PR を squash マージ**する（1 リリース = 1 コミット）。マージ直後は CI（`.github/workflows/sync-test-to-main.yml`）が `test` を `main` に force-with-lease で揃える。失敗時は手動で `reset --hard origin/main` する。詳細は [README.md ブランチ運用](../../README.md#ブランチ運用コントリビュータ向け) と [AGENTS.md](../../AGENTS.md)。

---

## マイルストーン一覧

| ID | 名称 | 目標 | ステータス |
|----|------|------|------------|
| M0 | 仕様策定 | SDD 仕様書整備 | **完了** |
| M1 | MVP | 単一ユーザー独立 .exe + **オーバーレイモード** + 自由配置カード + CRUD + 永続化 | **進行中** |
| M2 | 拡張 | 表示モード（ウィンドウ・デスクトップ）、3 列カンバン、列間移動、複数ボード、ラベル、検索 | 計画 |
| M3 | 本番化 | 認証、同期、クロスプラットフォーム | 計画 |

---

## M1: MVP

### スコープ定義

> **単一ユーザーの独立したデスクトップアプリケーション（`.exe`）**

| 区分 | 内容 |
|------|------|
| 含む | FR-001〜005, FR-007, FR-010, FR-014, FR-020, FR-021, FR-023, FR-024, FR-025, FR-026, FR-027, FR-028, FR-029（Should）, FR-030（Should）, FR-031（Must）, NFR-001〜008, NFR-011 |
| 含まない | ウィンドウモード（FR-018）、デスクトップモード（FR-019）、モード切替（FR-022）、列間移動（FR-006）、手動保存/再読み込み（FR-008/009） |

### 成果物

| 成果物 | パス |
|--------|------|
| 実行可能 exe | `dist/Petatto-Kanban.exe` |
| ソース | `src/petatto_kanban/` |
| SDD 仕様 | `docs/spec/` |
| CI | `.github/workflows/build-windows.yml`（PR: ビルド検証 / main マージ: GitHub Release） |

### 完了条件（Definition of Done）

- [ ] Must の全 FR が `verified`
- [ ] Must の全 NFR が `verified` または `implemented`（NFR-001 は手動確認）
- [ ] `python -m pytest` 全パス
- [ ] `python -m ruff check src tests` エラー 0
- [ ] Windows CI で exe ビルド成功
- [ ] [10-traceability-matrix.md](./10-traceability-matrix.md) 更新済み

### M1 進捗

| カテゴリ | 完了 | 合計 |
|----------|------|------|
| FR (Must) | 2 verified + 10 implemented | 12 |
| NFR (Must) | 6 verified + 2 specified + 1 implemented | 9 |
| US (Must) | 3 verified + 6 implemented | 9 |

---

## M2: 拡張

### 想定スコープ

| FR | 機能 |
|----|------|
| FR-018 | ウィンドウモード |
| FR-019 | デスクトップモード（透過・背面） |
| FR-022 | 表示モード切替 |
| FR-006 | 列間移動（3 列カンバン） |
| FR-011 | 複数ボード |
| FR-012 | 列カスタマイズ |
| FR-013 | ラベル |
| FR-015 | 検索・フィルタ |

### 着手条件

- M1 が完了（DoD 全項目 ✅）
- FR-010 の UI 契約（UC-003）と AC が `specified` 以上

---

## M3: 本番化

### 想定スコープ

- ユーザー認証（FR-017）
- クラウド同期
- macOS / Linux 検討
- WIP 制限（FR-016）

---

## 未決定事項

| # | 項目 | 選択肢 | 決定期限 | ステータス |
|---|------|--------|----------|------------|
| D-1 | M2 の DnD ライブラリ | tkinterdnd2 / PyQt 移行 / カスタム | M2 着手前 | Open |
| D-2 | 表示モード Win32 実装 | ctypes / pywin32 | M2 着手前 | Open |
| D-2 | GUI 自動テスト方針 | pytest + 仮想ディスプレイ / 手動のみ | M2 着手前 | Open |
| D-3 | スキーマバージョニング | なし / `schema_version` フィールド | M2 着手前 | Open |
| D-4 | 多言語対応 | 日本語のみ / i18n | M3 | Open |

### 決定済み

| # | 項目 | 決定 | 日付 | ADR |
|---|------|------|------|-----|
| D-✓1 | 実装言語 | Python 3.11+ | 2026-08-12 | ADR-001 |
| D-✓2 | GUI | tkinter | 2026-08-12 | ADR-001 |
| D-✓3 | 永続化 | JSON ファイル | 2026-08-12 | ADR-002 |
| D-✓4 | 配布形式 | PyInstaller .exe | 2026-08-12 | — |
| D-✓5 | 仕様形式 | SDD（docs/spec/） | 2026-08-12 | ADR-003 |
| D-✓6 | MVP カード移動 | コンボボックス（DnD は M2） | 2026-08-12 | — |
| D-✓7 | 初期スコープ | 単一ユーザーの独立デスクトップ .exe | 2026-08-12 | ADR-004 |
| D-✓8 | 対応 OS | Windows 11 以降 | 2026-08-12 | — |
| D-✓10 | ログオン時自動起動 | HKCU Run キー（値名 `Petatto-Kanban`） | 2026-08-14 | ADR-006 |
| D-✓11 | 新規カードショートカット | グローバルホットキー（既定 Ctrl+Shift+N） | 2026-08-14 | ADR-007 |
| D-✓12 | エラー診断 | ローカル `logs/` のみ。GitHub Issue 自動起票はしない | 2026-08-14 | ADR-008 |

---

## 改訂履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2026-08-12 | 初版（旧 SPECIFICATION.md より移行） |
| 2.0.0 | 2026-08-12 | SDD 形式リファクタリング、M1 進捗反映 |
| 2.1.0 | 2026-08-12 | 初期スコープを単一ユーザー独立 .exe と明確化 |
| 2.2.0 | 2026-08-12 | UI 表示モード 3 種を追加 |
| 2.3.0 | 2026-08-12 | ターゲット OS を Windows 11 以降に変更 |
| 2.4.0 | 2026-08-13 | GitHub Release 自動作成（main マージ時・バージョン同期 CI） |
| 2.5.0 | 2026-08-14 | M1 拡張に FR-026〜029 を明記。ADR-006（HKCU Run） |
| 2.6.0 | 2026-08-14 | M1 拡張に FR-030（ショートカット新規カード / 操作タブ） |
| 2.7.0 | 2026-08-14 | M1 拡張に FR-031（ローカルエラーログ）/ FR-032（GitHub Issue 任意起票） |
| 2.7.1 | 2026-08-14 | FR-032: 起票可否は設定「システム」タブで ON/OFF |
| 2.7.2 | 2026-08-14 | FR-032 GitHub Issue 自動起票を cancelled。診断は FR-031 のみ |
| 2.7.3 | 2026-08-14 | FR-031 実装（`system/error_log.py`） |
| 2.7.4 | 2026-08-14 | FR-031 仕様同期。パスと伏せ字を分離 |
| 2.8.0 | 2026-08-15 | カレンダー日付ボタンの外寸固定とテーマ対応ホバー（FR-014 / UC-008） |
| 2.8.1 | 2026-08-15 | FR-014 実装。日付配色を `due_date_calendar.py` に分離 |
| 2.8.2 | 2026-08-15 | ブランチ戦略 B: `test` → `main` は squash。直後に `test` を `main` へ同期 |
| 2.8.3 | 2026-08-15 | `test` の main 同期を `sync-test-to-main.yml` で自動化 |
