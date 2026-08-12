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
| 実装 | `src/petatto_kanban/storage.py` |

### ルートオブジェクト: Board

| フィールド | JSON 型 | 必須 | Python 型 | 説明 |
|------------|---------|------|-----------|------|
| `id` | string | ○ | `str` (UUID) | ボード一意識別子 |
| `name` | string | ○ | `str` | ボード名 |
| `columns` | array | ○ | `list[Column]` | 列の配列 |
| `created_at` | string | ○ | `datetime` | ISO 8601 形式 |
| `updated_at` | string | ○ | `datetime` | ISO 8601 形式 |

### ネスト: Column

| フィールド | JSON 型 | 必須 | Python 型 | 説明 |
|------------|---------|------|-----------|------|
| `id` | string | ○ | `str` (UUID) | 列一意識別子 |
| `name` | string | ○ | `str` | 列名 |
| `order` | number | ○ | `int` | 表示順（0 始まり） |
| `cards` | array | ○ | `list[Card]` | カードの配列 |

### ネスト: Card

| フィールド | JSON 型 | 必須 | Python 型 | 説明 |
|------------|---------|------|-----------|------|
| `id` | string | ○ | `str` (UUID) | カード一意識別子 |
| `title` | string | ○ | `str` | タイトル（空不可） |
| `description` | string | ○ | `str` | 説明（空文字可） |
| `order` | number | ○ | `int` | 列内表示順（0 始まり） |
| `created_at` | string | ○ | `datetime` | ISO 8601 形式 |
| `updated_at` | string | ○ | `datetime` | ISO 8601 形式 |

### 不変条件（Invariants）

| # | 条件 |
|---|------|
| INV-1 | `columns` は `order` 昇順でシリアライズされる |
| INV-2 | 各 `Column.cards` は `order` 昇順でシリアライズされる |
| INV-3 | ファイル不存在時、`Board.create_default()` の内容が使用される |
| INV-4 | 保存時に `board.updated_at` が現在時刻に更新される |

### サンプル

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Board",
  "columns": [
    {
      "id": "col-001",
      "name": "To Do",
      "order": 0,
      "cards": [
        {
          "id": "card-001",
          "title": "仕様書を SDD 形式に更新",
          "description": "docs/spec/ を整備",
          "order": 0,
          "created_at": "2026-08-12T11:00:00+00:00",
          "updated_at": "2026-08-12T11:30:00+00:00"
        }
      ]
    },
    {
      "id": "col-002",
      "name": "In Progress",
      "order": 1,
      "cards": []
    },
    {
      "id": "col-003",
      "name": "Done",
      "order": 2,
      "cards": []
    }
  ],
  "created_at": "2026-08-12T10:00:00+00:00",
  "updated_at": "2026-08-12T11:30:00+00:00"
}
```

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
| `columns` | 3 列（To Do, In Progress, Done）、order = 0, 1, 2 |

### Card 制約

| 属性 | 制約 |
|------|------|
| `title` | UI 層で空文字・空白のみを拒否 |
| `id` | 未指定時 UUID v4 自動生成 |

---

## M2 以降の拡張（草案）

| フィールド | 追加先 | マイルストーン |
|------------|--------|----------------|
| `wip_limit` | Column | M3 |
| `labels` | Card | M2 |
| `due_date` | Card | M2 |

スキーマ変更時は DC バージョンをインクリメントし、マイグレーション方針を追記する。

---

## DC-003: 表示設定スキーマ

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-021, FR-022 |
| 保存先 | `board.json` 内 `display_settings` または `%USERPROFILE%\.petatto-kanban\settings.json`（実装時決定） |
| マイルストーン | M2 |

### DisplaySettings

| フィールド | JSON 型 | 必須 | 説明 |
|------------|---------|------|------|
| `mode` | string | ○ | `"window"` \| `"desktop"` \| `"overlay"` |
| `monitor_index` | number | - | 表示先ディスプレイ（0 始まり）。`window` 時は未使用 |
| `window_geometry` | string | - | ウィンドウモード復帰用 `"WxH+X+Y"`（例: `960x540+100+100`） |

### 既定値

| フィールド | 既定値 |
|------------|--------|
| `mode` | `"window"` |
| `monitor_index` | `0`（プライマリ） |

### サンプル

```json
{
  "mode": "overlay",
  "monitor_index": 1,
  "window_geometry": "960x540+120+80"
}
```
