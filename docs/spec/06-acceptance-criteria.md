# 06 — 受け入れ基準

| 項目 | 内容 |
|------|------|
| ステータス | Active |
| 形式 | Given / When / Then（BDD） |

---

## 使い方

1. 実装前: 対象 FR の AC が `specified` 以上であることを確認
2. 実装後: 各 AC を満たすテストまたは手動検証を実施
3. 検証完了: [10-traceability-matrix.md](./10-traceability-matrix.md) のステータスを `verified` に更新

---

## FR-001 / FR-002: ボード・列表示

### AC-001-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-001 |
| 関連 US | US-001 |
| ステータス | verified |
| 検証 | 手動 |

```gherkin
Given アプリが起動していない
When ユーザーがアプリを起動する
Then タイトル "Petatto-Kanban" のウィンドウが表示される
And ヘッダーにボード名が表示される
And 3 列（To Do, In Progress, Done）が横並びで表示される
```

### AC-002-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-002 |
| 関連 US | US-001 |
| ステータス | verified |
| 検証 | 自動 |

```gherkin
Given 永続化ファイルが存在しない
When load_board() を呼び出す
Then 名前 "My Board" のボードが返る
And 3 列の名称が ["To Do", "In Progress", "Done"] である
```

**テスト**: `test_create_default_board_has_three_columns`, `test_load_missing_file_returns_default`

---

## FR-003: カード作成

### AC-003-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-003 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given To Do 列が表示されている
When ユーザーが「+ カードを追加」をクリックし、タイトル "新タスク" を入力する
Then To Do 列に "新タスク" カードが表示される
And データが board.json に保存される
```

### AC-003-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-003 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given カード追加ダイアログが開いている
When ユーザーが空のタイトルを入力する
Then カードは作成されない
```

---

## FR-004: カード編集

### AC-004-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-004 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given "旧タイトル" のカードが存在する
When ユーザーが「編集」からタイトル "新タイトル" と説明 "詳細" を保存する
Then カードに "新タイトル" と "詳細" が表示される
```

---

## FR-005: カード削除

### AC-005-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-005 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given "削除対象" のカードが存在する
When ユーザーが「削除」をクリックし、確認ダイアログで「はい」を選択する
Then カードが列から消える
And board.json からも削除されている
```

---

## FR-006: カード列間移動

### AC-006-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-006 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given "タスクA" が To Do 列にある
When ユーザーが移動先コンボボックスで "In Progress" を選択する
Then "タスクA" が In Progress 列に表示される
And To Do 列から "タスクA" が消える
```

---

## FR-007: データ永続化

### AC-007-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-007 |
| ステータス | verified |
| 検証 | 自動 |

```gherkin
Given カードを 1 件含むボードがある
When save_board() の後 load_board() を呼び出す
Then ボード名・列数・カードタイトルが一致する
```

**テスト**: `test_save_and_load_board`

### AC-007-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-007 |
| ステータス | verified |
| 検証 | 自動 |

```gherkin
Given Board オブジェクトがある
When board_to_dict() → board_from_dict() を実行する
Then 全属性が一致する
```

**テスト**: `test_board_roundtrip_dict`

### AC-007-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-007 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given ユーザーがカードを編集した
When ユーザーがウィンドウを閉じる
Then board.json に最新データが保存されている
```

---

## FR-008 / FR-009: 手動保存・再読み込み

### AC-008-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-008 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given ボードに未保存の変更がある
When ユーザーが「保存」をクリックする
Then "保存しました。" メッセージが表示される
```

### AC-009-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-009 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given board.json が外部で更新された
When ユーザーが「再読み込み」をクリックする
Then 画面が board.json の内容で更新される
```

---

## 非機能要件

### AC-NFR-001-01

| 属性 | 値 |
|------|-----|
| 関連 NFR | NFR-001 |
| ステータス | specified |
| 検証 | 手動（M1） |

```gherkin
Given 100 件のカードがあるボード
When ユーザーがカードを 1 件追加する
Then 操作が 1 秒以内に完了する
```

---

## M2 以降（プレースホルダー）

| ID | 関連 FR | ステータス |
|----|---------|------------|
| AC-010-01 | FR-010（DnD） | draft |
| AC-011-01 | FR-011（複数ボード） | draft |

M2 要件の詳細化時に AC を追加する。
