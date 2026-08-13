# 09 — アーキテクチャ

| 項目 | 内容 |
|------|------|
| ステータス | Active |
| ADR 形式 | 主要決定のみ記録 |

---

## 1. システム概要

**アーキテクチャ方針（M1）:** 単一ユーザーの独立したデスクトップアプリケーション。  
クライアント（`.exe`）とローカル JSON ファイルのみで構成し、サーバー層は存在しない。

```mermaid
flowchart TB
    subgraph Desktop["Windows PC（単一ユーザー）"]
        EXE["Petatto-Kanban.exe"]
        subgraph App["petatto_kanban"]
            UI["app.py (tkinter GUI)"]
            Models["models.py (Domain)"]
            Storage["storage.py (JSON I/O)"]
        end
        JSON["~/.petatto-kanban/board.json"]
    end
    EXE --> App
    Storage --> JSON
    UI --> Models
    UI --> Storage
```

---

## 2. 技術スタック（確定: M1）

| レイヤー | 技術 | 関連 NFR |
|----------|------|----------|
| 言語 | Python 3.11+ | — |
| GUI | tkinter | NFR-005 |
| 永続化 | JSON ファイル | NFR-003 |
| パッケージング | setuptools (`src` layout) | — |
| exe ビルド | PyInstaller | NFR-004 |
| テスト | pytest | NFR-007 |
| Lint | Ruff | NFR-006 |

コーディング規約: [PYTHON_CODING_RULES.md](../PYTHON_CODING_RULES.md)

---

## 3. ディレクトリ構成

```
petatto-kanban/
├── docs/
│   ├── SPECIFICATION.md          # SDD 索引
│   ├── PYTHON_CODING_RULES.md
│   └── spec/                     # SDD 仕様モジュール
│       ├── 01-vision-and-scope.md
│       ├── ...
│       └── 11-release-plan.md
├── src/petatto_kanban/
│   ├── __init__.py
│   ├── __main__.py               # エントリポイント
│   ├── app.py                    # GUI（プレゼンテーション）
│   ├── card_ui.py                # カードウィジェット参照・クリック判定
│   ├── due_date.py               # 期限表示・状態
│   ├── due_date_picker.py        # フロートカレンダー UI / ホスト
│   ├── menu_panel.py             # メニューパネル UI
│   ├── menu_panel_layout.py      # メニューパネル座標・ヒット判定
│   ├── new_card_placement.py     # 新規カード初期配置（tkinter 非依存）
│   ├── progress.py               # 進捗率ユーティリティ
│   ├── display/                  # 表示モード・モニター
│   │   ├── transparent.py        # 透過色・全画面シェル
│   │   ├── overlay.py            # オーバーレイ（最前面）
│   │   ├── desktop.py            # デスクトップ（本体背面）
│   │   ├── menu_panel_host.py    # メニューパネル透過 Toplevel（デスクトップ時最前面）
│   │   ├── desktop_board_controller.py  # 本体 Z オーダー昇格・降格
│   │   ├── foreground.py         # 他アプリ前面判定
│   │   ├── modes.py              # モード適用ディスパッチ
│   │   ├── mode_labels.py        # 設定 UI ラベル
│   │   ├── settings_dialog.py    # UC-006 設定ダイアログ（タブ UI シェル）
│   │   ├── settings_dialog_tabs.py  # タブ定義（表示 / テーマ / システム）
│   │   ├── settings_dialog_labels.py  # 設定 UI 文言（tkinter 非依存）
│   │   ├── settings_dialog_panels.py  # 各タブのウィジェット構築
│   │   ├── settings_actions.py   # 設定適用・終了確認・全カード削除
│   │   ├── ui_scale.py           # UI サイズプリセット・スケール係数（FR-026）
│   │   ├── ui_scale_labels.py    # UI サイズ UI ラベル
│   │   ├── card_layout.py        # カード基準寸法・黄金比（UC-003 / UC-009）
│   │   ├── ui_metrics.py         # UiMetrics 合成（FR-026 + FR-027）
│   │   ├── ui_font.py              # UI フォントプリセット（FR-027）
│   │   ├── ui_font_labels.py       # UI フォント UI ラベル
│   │   ├── ui_theme.py             # UI カラーテーマパレット（FR-028）
│   │   ├── ui_theme_labels.py      # UI カラーテーマ UI ラベル
│   │   ├── ui_chrome.py          # メニュー・期限パネルホスト再構築
│   ├── card_renderer.py          # カード UI 描画（UiMetrics）
│   │   ├── settings.py           # settings.json
│   │   └── monitors.py           # モニター列挙
│   ├── models.py                 # ドメインモデル
│   └── storage.py                # 永続化（インフラ）
├── tests/
├── scripts/
│   ├── build_exe.bat
│   └── build_exe.ps1
├── petatto-kanban.spec           # PyInstaller
├── pyproject.toml
└── .github/workflows/build-windows.yml
```

### レイヤー責務

| モジュール | 責務 | 依存 |
|------------|------|------|
| `models.py` | ドメインエンティティ、不変条件 | 標準ライブラリのみ |
| `storage.py` | JSON シリアライズ / デシリアライズ | `models` |
| `app.py` | UI 描画、ユーザー操作、永続化トリガ | `models`, `storage`, `card_ui`, `due_date*`, `progress`, `display`, `menu_panel`, `new_card_placement` |
| `display/transparent.py` | 透過色・全画面シェル（オーバーレイ/デスクトップ共通） | 標準ライブラリ + tkinter |
| `display/modes.py` | 表示モード適用のディスパッチ | `overlay`, `desktop`, `settings` |
| `display/menu_panel_host.py` | メニューパネル専用透過 Toplevel（デスクトップ時 `-topmost`） | tkinter, `transparent`, `settings` |
| `display/desktop_board_controller.py` | DM-DESKTOP-02/03 本体 Z オーダー制御 | tkinter, `desktop`, `foreground`, `menu_panel_host` |
| `display/foreground.py` | 前面ウィンドウのプロセス判定 | `transparent`, Windows API |
| `display/settings_dialog.py` | UC-006 設定ダイアログ（`ttk.Notebook` シェル・確定値組み立て） | tkinter, `mode_labels`, `settings_dialog_tabs`, `settings_dialog_labels`, `settings_dialog_panels`, `settings`, `monitors` |
| `display/settings_dialog_tabs.py` | タブラベル・タブ別項目定義 | 標準ライブラリのみ |
| `display/settings_dialog_labels.py` | 設定ダイアログ UI 文言 | 標準ライブラリのみ |
| `display/settings_dialog_panels.py` | 表示 / システムタブのウィジェット構築 | tkinter, `mode_labels`, `settings_dialog_labels`, `monitors` |
| `display/settings_actions.py` | 設定適用・終了確認・全カード削除（`app.py` から利用） | `settings_dialog`, `settings_dialog_labels`, `storage` |
| `display/ui_scale.py` | UI サイズプリセット・スケール係数（FR-026） | 標準ライブラリのみ |
| `display/ui_scale_labels.py` | UI サイズコンボボックス用ラベル | 標準ライブラリのみ |
| `display/card_layout.py` | カード基準寸法・黄金比・スケール（UC-003 / UC-009） | 標準ライブラリのみ |
| `display/ui_metrics.py` | `UiMetrics` 生成（ui_size + ui_font + card_layout 合成） | `ui_scale`, `ui_font`, `card_layout` |
| `card_renderer.py` | カード UI 描画（UiMetrics + UiThemePalette） | tkinter, `ui_metrics`, `ui_theme`, `due_date`, `progress` |
| `display/ui_chrome.py` | メニューパネル・期限パネルホストの再構築 | tkinter, `ui_metrics`, `ui_theme`, `menu_panel`, `due_date_picker` |
| `display/ui_font.py` | UI フォントプリセット・tkinter ファミリー解決（FR-027） | 標準ライブラリのみ |
| `display/ui_font_labels.py` | UI フォントコンボボックス用ラベル | 標準ライブラリのみ |
| `display/ui_theme.py` | UI カラーテーマパレット・トークン解決（FR-028） | 標準ライブラリのみ |
| `display/ui_theme_labels.py` | UI カラーテーマコンボボックス用ラベル | 標準ライブラリのみ |
| `display/mode_labels.py` | 表示モード UI ラベル | `settings` |
| `menu_panel.py` | メニューパネル UI（円形・NE アンカー・ホバー展開） | tkinter, `menu_panel_layout` |
| `menu_panel_layout.py` | メニューパネル座標・ヒット判定、`MenuPanelRect` | 標準ライブラリのみ |
| `new_card_placement.py` | 新規カード初期配置座標（UC-004 / FR-003） | `menu_panel_layout` |
| `card_ui.py` | カード UI 参照、二回離しクリック判定 | tkinter |
| `due_date_picker.py` | フロート期限パネル配置・外側クリック | `due_date`, `card_ui` |

---

## 4. アーキテクチャ決定記録（ADR）

### ADR-001: Python + tkinter 採用

| 項目 | 内容 |
|------|------|
| ステータス | Accepted |
| 日付 | 2026-08-12 |
| コンテキスト | Windows 11 以降のデスクトップ MVP、exe 配布、依存最小化 |
| 決定 | Python 3.11+ と tkinter を採用 |
| 理由 | 標準ライブラリのみで GUI 実現、PyInstaller 実績 |
| トレードオフ | DnD・モダン UI は制約あり（M2 で再評価） |

### ADR-002: JSON ファイル永続化

| 項目 | 内容 |
|------|------|
| ステータス | Accepted |
| 日付 | 2026-08-12 |
| コンテキスト | MVP はローカル完結、ネットワーク不要 |
| 決定 | `%USERPROFILE%\.petatto-kanban\board.json` |
| 理由 | シンプル、デバッグ容易、ポータブル |
| トレードオフ | 大量データ・同時編集には不向き |

### ADR-003: SDD 形式の仕様管理

| 項目 | 内容 |
|------|------|
| ステータス | Accepted |
| 日付 | 2026-08-12 |
| コンテキスト | 仕様と実装の乖離防止 |
| 決定 | `docs/spec/` にモジュール分割し SDD を採用 |
| 理由 | 要件 ID・受け入れ基準・トレーサビリティの明示 |
| トレードオフ | ドキュメント更新コスト増 |

### ADR-004: 単一ユーザー独立デスクトップアプリ（初期スコープ）

| 項目 | 内容 |
|------|------|
| ステータス | Accepted |
| 日付 | 2026-08-12 |
| コンテキスト | プロダクトの初期スコープを明確化 |
| 決定 | M1 MVP は **単一ユーザーの独立した `.exe` デスクトップアプリ** とする |
| 理由 | 開発範囲の限定、オフライン利用、配布の簡素化 |
| トレードオフ | チーム利用・同期は M3 まで提供しない |
| 関連 | NFR-008, [01-vision-and-scope.md §2](./01-vision-and-scope.md#2-初期スコープm1-mvpの定義) |

### ADR-005: Windows 11 以降をサポート対象とする

| 項目 | 内容 |
|------|------|
| ステータス | Accepted |
| 日付 | 2026-08-12 |
| コンテキスト | 表示モード・DWM / Win32 API の前提 OS を明確化 |
| 決定 | **サポート対象 OS は Windows 11 以降** とする |
| 理由 | 透過ウィンドウ・マルチディスプレイ・最新 DWM の動作を保証しやすい |
| トレードオフ | Windows 10 ユーザーは非サポート |
| 関連 | NFR-011 |

---

## 5. ビルド・配布

| 段階 | コマンド | 成果物 |
|------|----------|--------|
| 開発起動 | `python -m petatto_kanban` | — |
| テスト | `python -m pytest` | — |
| Lint | `python -m ruff check src tests` | — |
| exe ビルド | `scripts\build_exe.bat` | `dist/Petatto-Kanban.exe` |
| CI | GitHub Actions (`windows-latest`) | GitHub Release: `.exe` |

---

## 6. 将来アーキテクチャ（M3 草案）

| 要素 | 候補 |
|------|------|
| 同期 | REST API + PostgreSQL / Supabase |
| 認証 | OAuth / メール+パスワード |
| 設定 | SQLite への移行検討 |

M3 着手時に ADR を追加する。

---

## 4. 表示モード実装方針

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-018〜022 |
| 詳細仕様 | [12-display-modes.md](../spec/12-display-modes.md) |
| マイルストーン | M1（オーバーレイ・**デスクトップ**）/ M2（ウィンドウ・3 列切替） |

### Windows API 要件

| モード | 主要 API / 属性 |
|--------|----------------|
| ウィンドウ | 標準 `tk.Tk()`、`minsize` |
| デスクトップ | 本体: 全画面 geometry、`-transparentcolor`、`HWND_BOTTOM`。メニュー: 独立 Toplevel + `-topmost` |
| オーバーレイ | 全画面 geometry、Layered Window、`-topmost` / `WS_EX_TOPMOST`、クリック透過 |

### モジュール分割（計画）

| モジュール | 責務 |
|------------|------|
| `display/modes.py` | モード定義・状態遷移 |
| `display/win32.py` | Windows 固有の Z オーダー・透過・モニター列挙 |
| `app.py` | モード切替 UI、既存カンバン描画 |

### 技術的制約

- **対応 OS: Windows 11 以降**（Win32 / DWM API を前提）
- tkinter 単体では Z オーダー制御・クリック透過が不足するため、M2 では `ctypes` + Win32 API または `pywin32` の導入を検討
- マルチディスプレイ座標は `EnumDisplayMonitors` で取得
- NFR-008（ネットワーク不要）を維持 — 表示モード実装もローカル API のみ
