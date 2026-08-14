# Petatto-Kanban Python コーディングルール

| 項目 | 内容 |
|------|------|
| 対象 | 本リポジトリの Python ソースコード（`src/`, `tests/`） |
| Python バージョン | 3.11 以上 |
| 文書バージョン | 1.5.0 |
| 最終更新日 | 2026-08-14 |

---

## 1. 基本方針

- **仕様駆動開発（SDD）**に従う。機能追加・変更は先に [docs/spec/](../spec/) の仕様を更新する（[SPECIFICATION.md](../SPECIFICATION.md) 参照）。
- **読みやすさを最優先**する。賢い書き方より、意図が伝わる書き方を選ぶ。
- **標準ライブラリを優先**し、外部依存は必要最小限に留める（MVP では GUI に tkinter、永続化に JSON を使用）。
- **型ヒントを付ける**。関数の引数・戻り値、クラス属性に型を明示する。
- **1 ファイル 1 責務**を意識し、UI・ドメインロジック・永続化を分離する。

---

## 2. プロジェクト構成

```
src/petatto_kanban/
├── __init__.py       # パッケージ公開情報（__version__ 等）
├── __main__.py       # CLI / exe エントリポイント
├── app.py            # GUI アプリケーション
├── display/          # 表示モード・設定ダイアログ・UI メトリクス
├── system/           # OS 連携（自動起動・起動コマンド・ショートカット・ホットキー）
├── models.py         # ドメインモデル（Board, Column, Card）
└── storage.py        # データ永続化

tests/                # pytest テスト
scripts/              # ビルドスクリプト（Windows .exe）
```

### 配置ルール

| 種類 | 配置先 | 例 |
|------|--------|-----|
| ドメインモデル | `models.py` | `Board`, `Card` |
| 永続化・I/O | `storage.py` | JSON 読み書き |
| UI（tkinter） | `app.py`, `display/` | ウィンドウ、設定ダイアログ、カード描画 |
| OS 連携 | `system/` | 自動起動（winreg）、起動コマンド解決、ショートカット正規化、ホットキーセッション、Win32 ポンプ |
| テスト | `tests/test_*.py` | モデル・ストレージ・設定・自動起動・ショートカット・ホットキーの単体テスト |

---

## 3. 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| モジュール | `snake_case` | `storage.py` |
| クラス | `PascalCase` | `KanbanApp`, `Card` |
| 関数・メソッド | `snake_case` | `load_board`, `save_board` |
| 定数 | `UPPER_SNAKE_CASE` | `APP_TITLE`, `DATA_FILE_NAME` |
| プライベート | 先頭 `_` | `_render_card`, `_SettingsDialog` |
| 型エイリアス | `PascalCase` | `CardId = str`（必要時） |

---

## 4. 型ヒント

- すべての公開関数・メソッドに型ヒントを付ける。
- `from __future__ import annotations` をモジュール先頭に記述し、前方参照を簡潔にする。
- コレクションは `list[T]`, `dict[K, V]` 形式（Python 3.9+ スタイル）を使用する。
- `Optional[T]` より `T | None` を優先する。

```python
from __future__ import annotations

from pathlib import Path

from petatto_kanban.models import Board


def load_board(path: Path | None = None) -> Board:
    ...
```

---

## 5. docstring

- **公開モジュール・クラス・関数**に docstring を記述する。
- 形式は Google スタイルを基本とする（1 行概要 + 必要に応じて Args / Returns）。
- 自明な処理（getter 等）には docstring を省略してよい。

```python
def save_board(board: Board, path: Path | None = None) -> None:
    """ボードを JSON ファイルに保存する."""
    ...
```

---

## 6. インポート

- 順序: **標準ライブラリ → サードパーティ → ローカル（自プロジェクト）**
- 各グループの間は空行 1 行。
- ワイルドカードインポート（`from module import *`）は禁止。
- ローカルインポートは `petatto_kanban` パッケージ名からの絶対インポートを使用する。

```python
import json
from pathlib import Path

from petatto_kanban.models import Board, Card
```

---

## 7. フォーマット・Lint

| ツール | 用途 | 設定 |
|--------|------|------|
| **Ruff** | Lint + import 整理 | `pyproject.toml` の `[tool.ruff]` |
| **pytest** | テスト | `tests/` 配下 |

### 実行コマンド

```bash
# Lint
python -m ruff check src tests

# 自動修正（可能な範囲）
python -m ruff check src tests --fix

# テスト
python -m pytest
```

### スタイル要点

- 1 行の最大文字数: **100 文字**
- 文字列: ダブルクォート `"` を基本とする
- 末尾カンマ: 複数行のコレクション・引数では付ける

---

## 8. エラーハンドリング

- **握りつぶさない**。例外を無視する `except: pass` は禁止。
- ユーザー向け GUI では `messagebox` で分かりやすいメッセージを表示する。
- ファイル I/O では、MVP 段階では存在チェックとデフォルト値返却で足りる場合はシンプルに保つ。
- ログが必要になった段階で `logging` モジュールを導入する（print デバッグは本番コードに残さない）。
- アプリのエラーログ出力先は `%USERPROFILE%\.petatto-kanban\logs\`（[FR-031](./spec/03-functional-requirements.md#fr-031-ローカルエラーログ)）。GitHub トークンやカード本文はログに出さない。

---

## 9. GUI（tkinter）のルール

- UI 構築ロジックは `app.py` に集約する。
- 長いコールバックは `_` プレフィックス付きのプライベートメソッドに分割する。
- `lambda` は短いイベントバインディングに限定し、複雑な処理は名前付きメソッドにする。
- ウィンドウ終了時（`WM_DELETE_WINDOW`）にデータを保存する。

---

## 10. テスト

- **モデルと永続化**は必ず pytest でテストする。
- GUI の自動テストは Phase 2 以降で検討（MVP では手動確認）。
- テストファイル名: `test_<対象>.py`
- テスト関数名: `test_<期待する動作>`
- 一時ファイルは `tmp_path` フィクスチャを使用する。

```python
def test_save_and_load_board(tmp_path: Path) -> None:
    data_path = tmp_path / "board.json"
    ...
```

---

## 11. 依存関係の追加

- ランタイム依存（`[project] dependencies`）は慎重に追加する。MVP は標準ライブラリのみ。
- 開発専用（`[project.optional-dependencies] dev`）に pytest, ruff, pyinstaller を配置。
- 新規依存追加時は `pyproject.toml` を更新し、README に記載する。

---

## 12. Windows .exe ビルド

- ビルド定義: `petatto-kanban.spec`（PyInstaller）
- ローカルビルド: `scripts\build_exe.bat` または `scripts\build_exe.ps1`
- CI: `.github/workflows/build-windows.yml`（Windows runner で自動ビルド）
- exe のエントリポイント: `src/petatto_kanban/__main__.py`

### ビルド前チェックリスト

1. `python -m ruff check src tests` がパスすること
2. `python -m pytest` がパスすること
3. Windows 環境で `scripts\build_exe.bat` を実行すること

---

## 13. コミット前チェックリスト

- [ ] 型ヒントが付いている
- [ ] Ruff の Lint エラーがない
- [ ] 関連テストが追加・更新されている
- [ ] 公開 API に docstring がある
- [ ] 不要な `print` やデバッグコードを削除した

---

## 14. 改訂履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2026-08-12 | 初版作成（Python デスクトップアプリ + exe ビルド対応） |
| 1.1.0 | 2026-08-14 | `display/`・`system/` 配置を現行実装に同期 |
| 1.2.0 | 2026-08-14 | `system/shortcut.py` をホットキー登録から分離 |
| 1.3.0 | 2026-08-14 | `system/hotkey_pump.py` をホットキーセッションから分離 |
| 1.4.0 | 2026-08-14 | `display/card_frame.py` をカード基準寸法から分離 |
| 1.5.0 | 2026-08-14 | エラーログパス（FR-031）と秘密情報をログに出さないことを追記 |
