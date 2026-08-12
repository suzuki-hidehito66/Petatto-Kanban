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
| 関連 FR | FR-021, FR-024 |
| 保存先 | `%USERPROFILE%\.petatto-kanban\settings.json` |
| マイルストーン | M1 |

### DisplaySettings

| フィールド | JSON 型 | 必須 | 説明 |
|------------|---------|------|------|
| `mode` | string | ○ | `"window"` \| `"desktop"` \| `"overlay"` |
| `monitor_index` | number | - | 表示先ディスプレイ（0 始まり） |
| `window_geometry` | string | - | ウィンドウモード復帰用 `"WxH+X+Y"` |
| `confirm_delete` | boolean | ○ | カード削除時に確認ダイアログを表示するか |
| `menu_panel_x` | number | - | メニューパネル左上 X（未設定時はデフォルト位置） |
| `menu_panel_y` | number | - | メニューパネル左上 Y（未設定時はデフォルト位置） |

### 既定値

| フィールド | 既定値 |
|------------|--------|
| `mode` | `"overlay"` |
| `monitor_index` | `0`（プライマリ） |
| `confirm_delete` | `true` |

### サンプル

```json
{
  "mode": "overlay",
  "monitor_index": 1,
  "window_geometry": "960x540+120+80",
  "confirm_delete": true
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
