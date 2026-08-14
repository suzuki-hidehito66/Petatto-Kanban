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

## FR-001 / FR-002: オーバーレイ・カード表示

### AC-001-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-001, FR-020 |
| 関連 US | US-001, US-010 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given アプリが起動していない
When ユーザーがアプリを起動する
Then 指定ディスプレイ全画面のオーバーレイが表示される
And 背景は透過しカードとメニューパネルのみ不透明である
And メニューパネル（円形＜）が画面右上に表示される
And メニューパネルにディスプレイ選択 UI は表示されない
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
And cards は空配列である
```

**テスト**: `test_create_default_board_is_empty`, `test_load_missing_file_returns_default`

---

## FR-003: カード作成

### AC-003-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-003 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given メニューパネルが表示されている
When ユーザーがホバー時の「＋」をクリックして離す
Then タイトル "新しいタスク" のカードがメニューパネル直下・右端揃えに即座に表示される
And タイトルがインライン編集状態になり入力にフォーカスされる
And 入力ダイアログは表示されない
And データが board.json に保存される
```

### AC-003-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-003 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given メニューパネルが表示されている
When ユーザーがホバー時の「＋」を2回クリックして離す
Then タイトル "新しいタスク" のカードが2枚、1 枚目はメニューパネル直下・右端揃え、2 枚目はその位置から左下に少しずれた位置に表示される
And 2枚目追加時は1枚目のインライン編集が確定されたうえで2枚目が編集状態になる
And それぞれ board.json に保存される
```

---

## FR-004: カード名のインライン編集

### AC-004-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-004 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given "旧タイトル" のカードが存在する
When ユーザーがタイトルを2回クリックし、2回目にボタンを離す
When ユーザーが "新タイトル" を確定する
Then カードに "新タイトル" が表示される
```

### AC-004-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-004 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given カードのタイトルがインライン編集状態である
When ユーザーが同一カードの期限パネルをクリックする
Then タイトル編集が確定される
And カードに入力したタイトルが表示される
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
And confirm_delete が true である
When ユーザーがカードで右クリックを押下する
Then カードは削除されない
When ユーザーが右クリックを離す
Then 確認ダイアログが表示される
When ユーザーが「はい」を選択する
Then カードが画面から消える
And board.json からも削除されている
```

### AC-005-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-005, FR-024 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given confirm_delete が false に設定されている
When ユーザーがカードで右クリックを離す
Then 確認ダイアログなしでカードが削除される
And コンテキストメニューは表示されない
```

### AC-005-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-005 |
| 関連 UC | UC-006 |
| ステータス | implemented |
| 検証 | 手動 + 自動 |

```gherkin
Given ボードにカードが1枚以上存在する
And ユーザーが設定ダイアログの「システム」タブを表示している
When ユーザーが「全てのカードを削除」を押し確認ダイアログで「はい」を選ぶ
Then 全カードが削除される
And board.json に空の cards 配列が保存される
And 画面上のカードが消える
When カードが0枚の状態で「全てのカードを削除」を押す
Then 情報ダイアログが表示され削除は行われない
```

**テスト**: `test_board_clear_cards`, `test_settings_actions.py`

---

---

## FR-006: カード列間移動（M2）

### AC-006-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-006 |
| ステータス | deferred |
| 検証 | — |

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
Then ボード名・カード数・カードタイトルと x,y 座標が一致する
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

## FR-008 / FR-009: 手動保存・再読み込み（M2）

### AC-008-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-008 |
| ステータス | deferred |
| 検証 | — |

```gherkin
Given ボードに未保存の変更がある
When ユーザーが「保存」をクリックする
Then "保存しました。" メッセージが表示される
```

### AC-009-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-009 |
| ステータス | deferred |
| 検証 | — |

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
| ステータス | implemented |
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
| ステータス | implemented |
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
| ステータス | implemented |
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
| ステータス | deferred |
| 検証 | 手動（M2） |

```gherkin
Given アプリが起動した
When 表示モードがウィンドウモードである
Then タイトルバー付きの通常ウィンドウが表示される
And 背景は不透明である
And ウィンドウサイズを変更できる
```

**注記** M1 ではオーバーレイモードのみ提供。本 AC は M2（FR-018 実装時）で検証する。

---

## FR-010: カード位置ドラッグ

### AC-010-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-010 |
| 関連 US | US-012 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given "タスクA" カードが (100, 100) に表示されている
When ユーザーがカードをドラッグして (200, 150) に移動する
Then カードが新しい位置に表示される
And board.json の x,y が更新されている
```

---

## FR-025: カード進捗率

### AC-025-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-025 |
| 関連 US | US-014 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given 進捗率 30% のカードが表示されている
When ユーザーがカード上でマウスホイールを上に回す
Then 進捗率が 40% と表示される
And バーが左から 40% 分塗りつぶされる
And board.json の progress が 40 である
```

### AC-025-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-025 |
| 関連 US | US-014 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given 進捗率 95% のカードが表示されている
When ユーザーがカード上でマウスホイールを上に回す
Then 進捗率が 100% と表示される
When ユーザーがカード上でマウスホイールを下に回す
Then 進捗率が 90% と表示される
```

### AC-025-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-025 |
| 関連 US | US-014 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given カードが表示されている
When ユーザーが進捗バーを左クリックドラッグする
Then カード全体が画面上で移動する
When ユーザーが進捗バー上で右クリックして離す
Then カード削除処理が実行される
```

---

## FR-014: カード期限

### AC-014-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-014 |
| 関連 US | US-015 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given 期限なしのカードが表示されている
When ユーザーが期限パネルを2回クリックし、2回目にボタンを離す
Then カード外にフロートのカレンダー編集パネルが表示される
When ユーザーが日付を選択する
Then 期限パネルに YYYY/MM/DD 形式で表示される
And board.json に due_date が保存される
```

### AC-014-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-014 |
| 関連 US | US-015 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given 期限が本日のカードが表示されている
Then 期限パネルの背景が黄色系である
Given 期限が過去日のカードが表示されている
Then 期限パネルの背景が赤色系である
When ユーザーが期限編集 UI で「期限なし」を選択する
Then 期限パネルに「期限なし」と表示される
```

### AC-014-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-014 |
| 関連 US | US-015 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given ユーザーが期限編集のカレンダーパネルを開いている
Then 当日の日付ボタンが緑色で表示される
```

### AC-014-04

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-014 |
| 関連 US | US-015 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given ユーザーが期限編集のカレンダーパネルを開いている
When ユーザーがパネル外（例: カードのタイトル部分）をクリックする
Then 期限編集パネルが閉じる
And due_date は変更されない
```

---

## FR-019: デスクトップモード

### AC-019-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-019, FR-022 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given ユーザーが設定ダイアログを開いている
And ユーザーが「表示」タブを表示している
When 表示モードを「デスクトップ」に変更して OK する
Then 指定ディスプレイ全体にカンバンが全画面表示される
And オーバーレイモードと同様にカード・メニューパネルのみ不透明でそれ以外は透過である
And settings.json に mode が "desktop" として保存される
And 次回起動時にデスクトップモードで復元される
```

### AC-019-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-019 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given デスクトップモードでカンバンが表示されている
When ユーザーが別アプリ（例: ブラウザ）を起動または前面に出す
Then 別アプリのウィンドウがカンバン本体（カード等）より前面に表示される
And カンバン本体はデスクトップ（壁紙）より前面にあり、通常ウィンドウより背面である
And メニューパネルは別アプリより前面に表示され、常に操作可能である
And メニューパネルをアクティブにするとカード等を含む本体が一時的に通常ウィンドウより前面に出る
And メニュー非アクティブ後、本体は再び通常ウィンドウより背面に戻る
And 他アプリケーションをアクティブにすると昇格中の本体は即座に背面に戻る
And カードは本体が前面の間、または露出している間は操作可能である
And 透過領域のクリックは下層（デスクトップ）へ通る
```

---

## FR-020: オーバーレイモード

### AC-020-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-020 |
| ステータス | implemented |
| 検証 | 手動（M1） |

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
| ステータス | implemented |
| 検証 | 手動（M1） |

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
| ステータス | implemented |
| 検証 | 手動（M1） |

```gherkin
Given ユーザーが設定ダイアログを開いている
When 表示ディスプレイを変更して OK する
Then 選択したモニター上に全画面表示される
And settings.json に monitor_index が保存される
And 次回起動時に同じ設定が復元される
```

### AC-022-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-022 |
| ステータス | deferred |
| 検証 | 手動（M2） |

```gherkin
Given ユーザーがオーバーレイモードで作業している
When ウィンドウモードに切り替える
Then 通常ウィンドウ表示に戻る
And ボード上のカードデータは保持されている
```

**注記** ウィンドウモード切替は M2（FR-018 実装時）で検証する。

### AC-022-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-022, FR-019, FR-020 |
| ステータス | implemented |
| 検証 | 手動 |

```gherkin
Given ユーザーがオーバーレイモードで作業している
When 設定ダイアログで表示モードを「デスクトップ」に変更して OK する
Then デスクトップモードに切り替わる
And カードの位置・内容は保持されている
When 再度設定で「オーバーレイ」に変更して OK する
Then オーバーレイモードに戻り、カンバンは最前面に表示される
And settings.json の mode が更新されている
```

**注記** M1 拡張では設定ダイアログによるオーバーレイ ↔ デスクトップ切替を検証する。

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
Given オーバーレイモードでアプリが表示されている
When ユーザーがメニューパネルホバー時の「×」をクリックして離す
Then アプリが終了する
And board.json と settings.json に最新データが保存されている
```

### AC-023-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-023 |
| 関連 US | US-011 |
| ステータス | implemented |
| 検証 | 手動 + 自動 |

```gherkin
Given 設定ダイアログの「システム」タブで confirm_exit が true に設定されている
When ユーザーがメニューパネルの「×」をクリックして離す
Then 「アプリを終了しますか？」確認ダイアログが表示される
When ユーザーが「いいえ」を選ぶ
Then アプリは終了しない
When ユーザーが再度「×」で終了し「はい」を選ぶ
Then アプリが終了し board.json と settings.json が保存される
```

**テスト**: `test_save_and_load_confirm_exit`, `test_settings_dialog.py`, `test_settings_actions.py`

---

## FR-024: 削除確認設定

### AC-024-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-024 |
| 関連 US | US-013 |
| ステータス | implemented |
| 検証 | 自動 + 手動 |

```gherkin
Given 設定ダイアログが開いている
And ユーザーが「システム」タブを表示している
When ユーザーが「カード削除時に確認ダイアログを表示する」のチェックを外して OK する
Then settings.json の confirm_delete が false になる
And 次回のカード削除で確認ダイアログが表示されない
```

**テスト**: `test_save_and_load_display_settings`, `test_display_settings_roundtrip_dict`, `test_settings_dialog.py`

---

## FR-026: UI サイズ設定

### AC-026-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-026 |
| 関連 US | US-016 |
| 関連 UC | UC-006, UC-009 |
| ステータス | implemented |
| 検証 | 自動 + 手動 |

```gherkin
Given 設定ダイアログが開いている
And ユーザーが「表示」タブを表示している
When ユーザーが UI サイズを「大」に変更して OK する
Then settings.json の ui_size が "large" になる
And カードのフォント・最小サイズ・メニューパネル円ボタンが拡大表示される
And カードの x / y 座標は変更されない
```

**テスト**: `test_ui_scale.py`, `test_settings_dialog.py`, `test_display_settings.py`

### AC-026-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-026 |
| 関連 US | US-016 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json に ui_size が "small" で保存されている
When アプリを再起動する
Then 起動直後から UI が「小」サイズで描画される
```

**テスト**: `test_save_and_load_ui_size`, `test_ui_scale.py`, `test_display_settings.py`

### AC-026-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-026 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json の ui_size が不明な文字列または欠損している
When 表示設定を読み込む
Then ui_size は "medium"（標準）として扱われる
And スケール係数 1.0 が適用される
```

**テスト**: `test_display_settings_from_dict_invalid_ui_size`, `test_ui_scale.py`

### AC-026-04

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-026 |
| 関連 US | US-016 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json に ui_size が "xlarge" で保存されている
When アプリを再起動する
Then 起動直後から UI が「極大」サイズ（scale 1.25）で描画される
```

**テスト**: `test_save_and_load_ui_size`, `test_ui_scale.py`, `test_ui_scale_labels.py`

---

## FR-027: UI フォント設定

### AC-027-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-027 |
| 関連 US | US-017 |
| 関連 UC | UC-006, UC-010 |
| ステータス | implemented |
| 検証 | 自動 + 手動 |

```gherkin
Given 設定ダイアログが開いている
And ユーザーが「表示」タブを表示している
When ユーザーがフォントを「メイリオ」に変更して OK する
Then settings.json の ui_font が "meiryo" になる
And カードタイトル・メニューパネル・期限パネルが Meiryo で描画される
And カードの x / y 座標は変更されない
And UI サイズ（ui_size）のスケールは維持される
```

**テスト**: `test_ui_font.py`, `test_settings_dialog.py`, `test_settings_actions.py`

### AC-027-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-027 |
| 関連 US | US-017 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json に ui_font が "yu_gothic_ui" で保存されている
When アプリを再起動する
Then 起動直後から UI が Yu Gothic UI ファミリーで描画される
```

**テスト**: `test_save_and_load_ui_font`, `test_ui_font.py`

### AC-027-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-027 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json の ui_font が不明な文字列または欠損している
When 表示設定を読み込む
Then ui_font は "segoe_ui" として扱われる
And tkinter フォントファミリーは "Segoe UI" になる
```

**テスト**: `test_display_settings_from_dict_invalid_ui_font`, `test_ui_font.py`

---

## FR-028: UI カラーテーマ設定

### AC-028-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-028 |
| 関連 US | US-018 |
| 関連 UC | UC-006, UC-011 |
| ステータス | implemented |
| 検証 | 自動 + 手動 |

```gherkin
Given 設定ダイアログが開いている
And ユーザーが「テーマ」タブを表示している
When ユーザーがカラーテーマを「ダーク」に変更して OK する
Then settings.json の ui_theme が "dark" になる
And カード背景が暗色・タイトル文字が明色で描画される
And メニューパネルの円ボタンがテーマ色で描画される
And カード上の期限パネルで当日は黄・超過は赤のまま表示される
And 進捗バーの塗り色は 0%≈赤 / 50%≈黄 / 100%≈緑のままである
And カードの x / y 座標は変更されない
```

**テスト**: `test_ui_theme.py`, `test_settings_dialog.py`, `test_settings_actions.py`

### AC-028-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-028 |
| 関連 US | US-018 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json に ui_theme が "forest" で保存されている
When アプリを再起動する
Then 起動直後から UI が forest テーマの配色で描画される
```

**テスト**: `test_save_and_load_ui_theme`, `test_ui_theme.py`

### AC-028-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-028 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json の ui_theme が不明な文字列または欠損している
When 表示設定を読み込む
Then ui_theme は "default" として扱われる
And 配色は default テーマ（現行既定）になる
```

**テスト**: `test_display_settings_from_dict_invalid_ui_theme`, `test_ui_theme.py`

---

## FR-029: Windows ログオン時自動起動

### AC-029-01

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-029 |
| ステータス | implemented |
| 検証 | 自動 + 手動（Windows） |

```gherkin
Given ユーザーが Windows 11 上で Petatto-Kanban を実行している
When 設定ダイアログ「システム」タブで「Windows ログオン時に自動起動する」を ON にして OK する
Then settings.json の launch_at_login が true になる
And HKCU\Software\Microsoft\Windows\CurrentVersion\Run に Petatto-Kanban エントリが作成される
```

**テスト**: `test_auto_start.py`, `test_display_settings.py`, `test_settings_dialog.py` + 手動

### AC-029-02

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-029 |
| ステータス | implemented |
| 検証 | 自動 + 手動（Windows） |

```gherkin
Given launch_at_login が true でレジストリにエントリがある
When ユーザーが同設定を OFF にして OK する
Then settings.json の launch_at_login が false になる
And Run キーから Petatto-Kanban エントリが削除される
```

**テスト**: `test_auto_start.py`, `test_settings_actions.py` + 手動

### AC-029-03

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-029 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json に launch_at_login フィールドがない
When 表示設定を読み込む
Then launch_at_login は false として扱われる
```

**テスト**: `test_default_display_settings_is_overlay_mode`, `test_display_settings.py`

### AC-029-04

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-029 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given アプリが Windows 以外の OS で動作している
When 設定ダイアログ「システム」タブを開く
Then 「Windows ログオン時に自動起動する」チェックボックスは無効である
And apply_auto_start_setting はレジストリを変更しない
```

**テスト**: `test_is_auto_start_supported_on_linux`, `test_settings_dialog.py` + 手動（Windows では有効）

### AC-029-05

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-029 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given settings.json の launch_at_login が true
When アプリを起動する
Then Run キーの Petatto-Kanban コマンド行が現在の実行パスで再書き込みされる
```

```gherkin
Given settings.json の launch_at_login が false
When アプリを起動する
Then Run キーは変更されない
```

**テスト**: `test_sync_auto_start_from_settings_registers_when_enabled`, `test_sync_auto_start_from_settings_skips_when_disabled`

### AC-029-06

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-029 |
| ステータス | implemented |
| 検証 | 自動 |

```gherkin
Given ユーザーが設定ダイアログで表示モードと launch_at_login を同時に変更した
When レジストリへの反映が失敗する
Then エラーメッセージが表示される
And メモリ上の DisplaySettings はダイアログ確定前の値に戻る
And settings.json は更新されない
And 「設定を保存しました」は表示されない
```

**テスト**: `test_persist_dialog_result_rolls_back_all_fields_on_auto_start_failure`

---

## M2 以降（プレースホルダー）

| ID | 関連 FR | ステータス |
|----|---------|------------|
| AC-011-01 | FR-011（複数ボード） | draft |

M2 要件の詳細化時に AC を追加する。
