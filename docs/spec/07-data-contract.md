# 07 — データ契約

| 項目 | 内容 |
|------|------|
| ステータス | Active |

---

## DC-001: board.json スキーマ

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-007 |
| ファイルパス | `%USERPROFILE%\.petatto-kanban\board.json` |
| エンコーディング | UTF-8 |
| スキーマバージョン | `5` |
| 実装 | `src/petatto_kanban/storage.py` |

### ルートオブジェクト: Board

| フィールド | JSON 型 | 必須 | Python 型 | 説明 |
|------------|---------|------|-----------|------|
| `schema_version` | number | ○ | `int` | スキーマバージョン（現在 `5`） |
| `id` | string | ○ | `str` (UUID) | ボード一意識別子 |
| `name` | string | ○ | `str` | ボード名 |
| `cards` | array | ○ | `list[Card]` | 画面上のカード配列 |
| `created_at` | string | ○ | `datetime` | ISO 8601 形式 |
| `updated_at` | string | ○ | `datetime` | ISO 8601 形式 |

### ネスト: Card

| フィールド | JSON 型 | 必須 | Python 型 | 説明 |
|------------|---------|------|-----------|------|
| `id` | string | ○ | `str` (UUID) | カード一意識別子 |
| `title` | string | ○ | `str` | タイトル（空不可） |
| `x` | number | ○ | `int` | 画面上の X 座標（px） |
| `y` | number | ○ | `int` | 画面上の Y 座標（px） |
| `progress` | number | ○ | `int` | 進捗率 0〜100 |
| `due_date` | string \| null | - | `date \| None` | 期限（`YYYY-MM-DD`）。未設定時 `null` |
| `created_at` | string | ○ | `datetime` | ISO 8601 形式 |
| `updated_at` | string | ○ | `datetime` | ISO 8601 形式 |

### 不変条件（Invariants）

| # | 条件 |
|---|------|
| INV-1 | ファイル不存在時、`Board.create_default()` の内容が使用される（空の `cards`） |
| INV-2 | 保存時に `board.updated_at` が現在時刻に更新される |
| INV-3 | 旧スキーマ（`columns` / `description` 付き cards）読み込み時は現行 Card に変換し、`description` は破棄 |
| INV-4 | `progress` 未指定の旧 cards は `0` として読み込む |
| INV-5 | `due_date` 未指定の旧 cards は `null`（期限なし）として読み込む |

### サンプル

```json
{
  "schema_version": 5,
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Board",
  "cards": [
    {
      "id": "card-001",
      "title": "仕様書を SDD 形式に更新",
      "x": 120,
      "y": 80,
      "progress": 40,
      "due_date": "2026-08-20",
      "created_at": "2026-08-12T11:00:00+00:00",
      "updated_at": "2026-08-12T11:30:00+00:00"
    }
  ],
  "created_at": "2026-08-12T10:00:00+00:00",
  "updated_at": "2026-08-12T11:30:00+00:00"
}
```

### レガシーマイグレーション（schema_version なし / columns 形式）

旧 `board.json` に `columns` 配列のみが存在する場合、読み込み時に各列・カードを格子状座標へ変換する。

| 変換ルール | 値 |
|------------|-----|
| 列 index | `x = 80 + column_index * 260` |
| カード index | `y = 80 + card_index * 130` |

---

## DC-002: ドメインモデル契約

| 属性 | 値 |
|------|-----|
| 実装 | `src/petatto_kanban/models.py` |

### Board.create_default()

| 属性 | 値 |
|------|-----|
| 戻り値 | `Board` |
| `name` | `"My Board"` |
| `cards` | 空配列 `[]` |

### Card 制約

| 属性 | 制約 |
|------|------|
| `title` | UI 層で空文字・空白のみを拒否 |
| `progress` | 0〜100 の整数。未指定時 `0` |
| `due_date` | 未指定時 `None`（期限なし） |
| `x`, `y` | 未指定時 `120, 120` |
| `id` | 未指定時 UUID v4 自動生成 |

---

## DC-003: 表示設定スキーマ

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-021, FR-024, FR-023, FR-026, FR-027, FR-028, FR-029, FR-030 |
| 保存先 | `%USERPROFILE%\.petatto-kanban\settings.json` |
| マイルストーン | M1 |

### DisplaySettings

| フィールド | JSON 型 | 必須 | 説明 |
|------------|---------|------|------|
| `mode` | string | ○ | `"overlay"` \| `"desktop"` \| `"window"` | M1 拡張: `overlay` / `desktop` を設定ダイアログで切替 |
| `monitor_index` | number | - | 表示先ディスプレイ（0 始まり） |
| `window_geometry` | string | - | ウィンドウモード復帰用 `"WxH+X+Y"` |
| `confirm_delete` | boolean | ○ | カード削除時に確認ダイアログを表示するか |
| `confirm_exit` | boolean | ○ | アプリ終了時に確認ダイアログを表示するか |
| `menu_panel_x` | number | - | メニューパネル左上 X（保存時の展開状態に依存。未設定時デフォルト） |
| `menu_panel_y` | number | - | メニューパネル左上 Y |
| `ui_size` | string | ○ | UI サイズプリセット: `"small"` \| `"medium"` \| `"large"` \| `"xlarge"`（FR-026） |
| `ui_font` | string | ○ | UI フォントプリセット: `"segoe_ui"` \| `"meiryo"` \| `"yu_gothic_ui"` \| `"ms_gothic"`（FR-027） |
| `ui_theme` | string | ○ | UI カラーテーマ: `"default"` \| `"dark"` \| ...（FR-028） |
| `launch_at_login` | boolean | ○ | Windows ログオン時に自動起動するか（FR-029） |
| `shortcuts` | object | ○ | キーボードショートカット割り当て（FR-030） |

#### shortcuts オブジェクト

| フィールド | JSON 型 | 必須 | 説明 |
|------------|---------|------|------|
| `new_card` | string | ○ | 新規カード作成のコード。既定 `"Ctrl+Shift+N"` |

**コードの正規形:** `Ctrl` / `Alt` / `Shift` をこの順で `+` 連結し、末尾にキー（`A`〜`Z` / `0`〜`9` / `F1`〜`F12`）。例: `"Ctrl+Shift+N"`。修飾キーが 1 つ以上必須。不正・欠損時は `"Ctrl+Shift+N"`。

### 既定値

| フィールド | 既定値 |
|------------|--------|
| `mode` | `"overlay"` |
| `monitor_index` | `0`（プライマリ） |
| `confirm_delete` | `true` |
| `confirm_exit` | `false` |
| `ui_size` | `"medium"` |
| `ui_font` | `"segoe_ui"` |
| `ui_theme` | `"default"` |
| `launch_at_login` | `false` |
| `shortcuts.new_card` | `"Ctrl+Shift+N"` |

### ui_font と tkinter フォント名

| ui_font（JSON） | UI ラベル | tkinter ファミリー名 |
|-----------------|-----------|----------------------|
| `segoe_ui` | Segoe UI | `Segoe UI` |
| `meiryo` | メイリオ | `Meiryo` |
| `yu_gothic_ui` | 游ゴシック | `Yu Gothic UI` |
| `ms_gothic` | MS ゴシック | `MS Gothic` |

不正値・欠損時は `segoe_ui` / `Segoe UI` にフォールバックする。OS に指定ファミリーが無い場合も `Segoe UI` にフォールバックする。

### ui_size とスケール係数

| ui_size（JSON） | UI ラベル | scale |
|-----------------|-----------|-------|
| `small` | 小 | 0.85 |
| `medium` | 標準 | 1.0 |
| `large` | 大 | 1.15 |
| `xlarge` | 極大 | 1.25 |

不正値・欠損時は `medium` / `1.0` にフォールバックする。

### ui_theme と設定 UI ラベル

| ui_theme（JSON） | 設定 UI ラベル |
|------------------|----------------|
| `default` | Default |
| `dark` | ダーク |
| `sandy` | サンディ |
| `forest` | フォレスト |
| `fancy` | ファンシー |
| `ocean` | オーシャン |
| `sunset` | サンセット |
| `slate` | スレート |
| `rose` | ローズ |
| `midnight` | ミッドナイト |

不正値・欠損時は `default` にフォールバックする。

### サンプル

```json
{
  "mode": "overlay",
  "monitor_index": 1,
  "window_geometry": "960x540+120+80",
  "confirm_delete": true,
  "confirm_exit": false,
  "ui_size": "medium",
  "ui_font": "segoe_ui",
  "ui_theme": "default",
  "launch_at_login": false,
  "shortcuts": {
    "new_card": "Ctrl+Shift+N"
  }
}
```

---

## M2 以降の拡張（草案）

| フィールド | 追加先 | マイルストーン |
|------------|--------|----------------|
| `columns` | Board | M2（3 列カンバン再導入時） |
| `labels` | Card | M2 |
| `wip_limit` | Column | M3 |

スキーマ変更時は `schema_version` をインクリメントし、マイグレーション方針を追記する。

---

## DC-004: エラーログ

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-031 |
| ディレクトリ | `%USERPROFILE%\.petatto-kanban\logs\` |
| エンコーディング | UTF-8 |
| 実装 | （未実装）`system/error_log.py` |

### ログファイル

| 項目 | 仕様 |
|------|------|
| ファイル名 | `petatto-kanban-YYYY-MM-DD.log`（ローカル日付） |
| ローテーション | 日次。起動時に 14 日より古いファイルを削除してよい |
| 書き込み | 追記。1 行または複数行のスタックトレース付きレコード |
| 最低フィールド | 時刻（ISO 8601）、レベル、ロガー名、メッセージ。例外時はトレースバック |

**不変条件**

| # | 条件 |
|---|------|
| INV-L1 | ディレクトリ不存在時は作成する。作成失敗時はアプリを落とさない |
| INV-L2 | 認証情報・環境変数の秘密はログに出さない |
| INV-L3 | カードタイトル・ボード JSON 本文はログに出さない |
| INV-L4 | ユーザーホームディレクトリは `~` に置換してよい |

### アプリデータディレクトリ（参考）

```
%USERPROFILE%\.petatto-kanban\
├── board.json
├── settings.json
└── logs\
    └── petatto-kanban-YYYY-MM-DD.log
```
