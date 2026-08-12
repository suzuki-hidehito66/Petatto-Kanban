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

### AC-NFR-008-01

| 属性 | 値 |
|------|-----|
| 関連 NFR | NFR-008 |
| ステータス | verified |
| 検証 | 自動（依存関係）+ コードレビュー |

```gherkin
Given M1 MVP のソースコードと pyproject.toml
When ランタイム依存とネットワーク呼び出しを確認する
Then [project] dependencies が空である
And 認証・HTTP クライアント等のネットワークコードが存在しない
```

### AC-NFR-008-02

| 属性 | 値 |
|------|-----|
| 関連 NFR | NFR-008 |
| ステータス | specified |
| 検証 | 手動（M1） |

```gherkin
Given ネットワークが切断された Windows PC
When ユーザーが Petatto-Kanban.exe を起動する
Then カードの作成・編集・移動・保存がすべて正常に動作する
And 外部サービスへの接続を要求されない
```

### AC-NFR-011-01

| 属性 | 値 |
|------|-----|
| 関連 NFR | NFR-011 |
| ステータス | specified |
| 検証 | 手動 + CI |

```gherkin
Given Windows 11 以降がインストールされた PC
When ユーザーが Petatto-Kanban.exe を起動する
Then アプリが正常に起動し M1 機能が利用できる
```

---

## FR-018: ウィンドウモード

### AC-018-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-018 |
| 関連 US | US-008 |
| ステータス | verified |
| 検証 | 手動 |

```gherkin
Given アプリが起動した
When 表示モードがウィンドウモードである
Then タイトルバー付きの通常ウィンドウが表示される
And 背景は不透明である
And ウィンドウサイズを変更できる
```

---

## FR-019: デスクトップモード

### AC-019-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-019 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given アプリが起動した
When 初回起動または設定未保存
Then デスクトップモードで指定ディスプレイに全画面表示される
And 背景透過でデスクトップが見える
```

### AC-019-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-019 |
| ステータス | implemented |
| 検証 | 手動（M1） |

```gherkin
Given デスクトップモードでカンバンが表示されている
When ユーザーが別アプリ（例: エクスプローラー）を起動する
Then 別アプリのウィンドウがカンバンより前面に表示される
And カンバン UI 部分は引き続き操作可能である
```

---

## FR-020: オーバーレイモード

### AC-020-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-020 |
| ステータス | specified |
| 検証 | 手動（M2） |

```gherkin
Given 複数ディスプレイが接続されている
When ユーザーがオーバーレイモードを選択しディスプレイ 1 を指定する
Then ディスプレイ 1 全体にカンバンが表示される
And カンバン UI 以外の領域は透過し下のウィンドウが見える
```

### AC-020-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-020 |
| ステータス | specified |
| 検証 | 手動（M2） |

```gherkin
Given オーバーレイモードでカンバンが表示されている
And 下に別アプリのウィンドウがある
When ユーザーが別アプリを操作する
Then カンバンは常に最前面に表示されたままである
And 透過領域をクリックすると下のアプリが操作できる
```

---

## FR-021 / FR-022: ディスプレイ指定・モード切替

### AC-021-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-021 |
| ステータス | specified |
| 検証 | 手動（M2） |

```gherkin
Given ユーザーがデスクトップまたはオーバーレイモードを選択した
When ディスプレイ一覧からモニターを選択する
Then 選択したモニター上に全画面表示される
And 次回起動時に同じ設定が復元される
```

### AC-022-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-022 |
| ステータス | specified |
| 検証 | 手動（M2） |

```gherkin
Given ユーザーがオーバーレイモードで作業している
When ウィンドウモードに切り替える
Then 通常ウィンドウ表示に戻る
And ボード上のカードデータは保持されている
```

---

## FR-023: アプリ終了

### AC-023-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-023 |
| 関連 US | US-011 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given デスクトップモードでアプリが表示されている
When ユーザーがヘッダー右上の「×」をクリックする
Then アプリが終了する
And board.json と settings.json に最新データが保存されている
```

---

## M2 以降（プレースホルダー）

| ID | 関連 FR | ステータス |
|----|---------|------------|
| AC-010-01 | FR-010（DnD） | draft |
| AC-011-01 | FR-011（複数ボード） | draft |

M2 要件の詳細化時に AC を追加する。
