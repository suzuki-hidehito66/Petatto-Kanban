# 03 — 機能要件

| 項目 | 内容 |
|------|------|
| ステータス | Active |
| マイルストーン | M1 MVP |

---

## スコープ前提

本ドキュメントの M1 要件は、以下の初期スコープ定義に従う。

> **単一ユーザーの独立したデスクトップアプリケーション（`.exe`）**

- ネットワーク API・ユーザー認証・マルチユーザー機能は M1 に含めない
- データは利用者の PC 内にのみ保存する（エラーログもローカル、[FR-031](#fr-031-ローカルエラーログ)）

参照: [01-vision-and-scope.md §2](./01-vision-and-scope.md#2-初期スコープm1-mvpの定義)

---

## 要件一覧サマリー

| ID | 機能 | 優先度 | ステータス | マイルストーン |
|----|------|--------|------------|----------------|
| [FR-001](#fr-001-オーバーレイボード表示) | オーバーレイボード表示 | Must | implemented | M1 |
| [FR-002](#fr-002-カード表示) | カード表示（自由配置） | Must | implemented | M1 |
| [FR-003](#fr-003-カード作成) | カード作成 | Must | implemented | M1 |
| [FR-004](#fr-004-カード名のインライン編集) | カード名インライン編集 | Must | implemented | M1 |
| [FR-005](#fr-005-カード削除) | カード削除 | Must | implemented | M1 |
| [FR-007](#fr-007-データ永続化) | データ永続化 | Must | verified | M1 |
| [FR-010](#fr-010-カード位置ドラッグ) | カード位置ドラッグ | Must | implemented | M1 |
| [FR-020](#fr-020-オーバーレイモード) | オーバーレイモード | Must | implemented | M1 |
| [FR-021](#fr-021-ディスプレイ指定) | ディスプレイ指定 | Must | implemented | M1 |
| [FR-023](#fr-023-アプリ終了) | アプリ終了（×ボタン） | Must | implemented | M1 |
| [FR-024](#fr-024-削除確認設定) | 削除確認設定 | Must | implemented | M1 |
| [FR-025](#fr-025-カード進捗率) | カード進捗率 | Must | implemented | M1 |
| [FR-014](#fr-014-カード期限) | カード期限 | Must | implemented | M1 |
| [FR-008](#fr-008-手動保存) | 手動保存 | Should | deferred | M2 |
| [FR-009](#fr-009-再読み込み) | 再読み込み | Should | deferred | M2 |
| [FR-019](#fr-019-デスクトップモード) | デスクトップモード | Should | implemented | M1 拡張 |
| [FR-018](#fr-018-ウィンドウモード) | ウィンドウモード | Should | deferred | M2 |
| [FR-022](#fr-022-表示モード切替) | 表示モード切替 | Should | implemented | M1 拡張 / M2 |
| [FR-026](#fr-026-uiサイズ設定) | UI サイズ設定 | Must | implemented | M1 拡張 |
| [FR-027](#fr-027-uiフォント設定) | UI フォント設定 | Must | implemented | M1 拡張 |
| [FR-028](#fr-028-uiカラーテーマ設定) | UI カラーテーマ設定 | Must | implemented | M1 拡張 |
| [FR-029](#fr-029-windowsログオン時自動起動) | Windows ログオン時自動起動 | Should | implemented | M1 拡張 |
| [FR-030](#fr-030-キーボードショートカットで新規カード作成) | キーボードショートカットで新規カード作成 | Should | implemented | M1 拡張 |
| [FR-031](#fr-031-ローカルエラーログ) | ローカルエラーログ | Must | implemented | M1 拡張 |
| [FR-032](#fr-032-github-issue-任意起票) | GitHub Issue 任意起票 | Should | cancelled | — |
| FR-006 | カード列間移動 | Should | deferred | M2 |
| FR-011 | 複数ボード | Could | deferred | M2 |
| FR-012 | 列のカスタマイズ | Could | deferred | M2 |
| FR-013 | ラベル | Could | deferred | M2 |
| FR-015 | 検索・フィルタ | Could | deferred | M2 |
| FR-016 | WIP 制限 | Won't (M2) | deferred | M3 |
| FR-017 | ユーザー認証 | Won't (M2) | deferred | M3 |

---

## M1 MVP 要件詳細

### FR-001: オーバーレイボード表示

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-001, US-010 |
| 関連 AC | AC-001-01, AC-020-01 |
| 実装 | `src/petatto_kanban/app.py`, `display/overlay.py` |

**説明**  
アプリ起動時、`settings.json` の `mode` に従い **オーバーレイモード** または **デスクトップモード** で指定ディスプレイ全画面にボードを表示する。未設定時はオーバーレイモード。

**制約**
- 背景は透過。カードとメニューパネルのみ不透明
- 透過領域はクリック透過（下のアプリまたはデスクトップを操作可能）
- オーバーレイ時は常に最前面。デスクトップ時は [FR-019](#fr-019-デスクトップモード) の Z オーダー（**メニューパネルのみ最前面**）

---

### FR-002: カード表示

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-001 |
| 関連 AC | AC-002-01, AC-002-02 |
| 実装 | `src/petatto_kanban/models.py`, `app.py`, `card_renderer.py`, `display/card_layout.py`, `display/card_frame.py` |

**説明**  
保存済みの座標 `(x, y)` にカードを配置して表示する。列レイアウトは M1 では使用しない。

**制約**
- 各カードは `place(x, y)` で画面上に配置
- **タイトルのみ**表示（説明フィールドは M1 では使用しない）
- タイトルは枠線付きの内側フレーム（`relief=GROOVE`, `bd=1`）で囲む
- 進捗率（0〜100%）をバーで表示し、左から進捗に応じた色で塗りつぶす（FR-025）
- 期限パネルを表示（FR-014）。期限なし / 日付表示、状態に応じた背景色
- カード枠はタイトル表示領域より大きくなるよう、最小サイズ（幅 175px・高さ 108px、横長黄金比 φ、medium 時フォント 10pt）を下限とする
- **幅は最小幅に固定**する。タイトルに改行・折り返しがあるときは **高さのみ**内容に合わせて拡張し、期限パネルと進捗バーが隠れないようにする
- 基準寸法・黄金比は `display/card_layout.py`、枠サイズ決定は `display/card_frame.py` に分離する

---

### FR-003: カード作成

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-002, US-020 |
| 関連 AC | AC-003-01, AC-003-02 |
| 実装 | `src/petatto_kanban/app.py`, `menu_panel.py`, `new_card_placement.py` |

**説明**  
メニューパネルホバー時の **＋** ボタンをクリックして離す（`<ButtonRelease-1>`）と、即座に新しいカードを1枚追加する。

**制約**
- 初期タイトルは既定値 `新しいタスク`（`DEFAULT_NEW_CARD_TITLE`）
- 新規カードはメニューパネル直下・右端基準から `inset_x`（128px）左に配置
- パネル下端からの余白は 2px
- 配置後はモニター範囲内にクランプし、画面外に生成しない
- 連続追加時は 1 枚ごとに左 12px・下 12px ずつずらす
- 配置基準は `MenuPanel.bounds()` が返す現在のパネル矩形（展開/収納・ドラッグ移動後の位置を反映）
- 追加直後は FR-004 のインライン編集状態で開始し、タイトル入力にフォーカス
- 入力ダイアログは表示しない
- キーボードショートカットからの作成は [FR-030](#fr-030-キーボードショートカットで新規カード作成)。配置・初期タイトル・インライン編集は本要件と同一

---

### FR-004: カード名のインライン編集

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-003 |
| 関連 AC | AC-004-01, AC-004-02 |
| 実装 | `src/petatto_kanban/app.py` |

**説明**  
タイトルで **クリック→離す→クリック→離す**（2回目の `<ButtonRelease-1>`）でインライン編集する。

**制約**
- タイトル枠・ラベル上で 2回目の `<ButtonRelease-1>`、または FR-003 によるカード追加直後に `Entry` に切り替え
- Enter またはフォーカスアウトで確定、`Escape` でキャンセル
- 編集中に同一カードの **タイトル以外**（期限パネル・進捗バー・カード枠など）をクリックした場合も確定して編集を終了
- カード追加・設定・終了時は進行中の編集を **確定してから** 処理する（AC-003-02, AC-007-03）
- タイトルは必須（空文字・空白のみは拒否）
- 確定時に `updated_at` を更新し `board.json` に保存
- 短いクリック＋ドラッグは移動、2回目の離しで編集開始（期限パネルと同様）

---

### FR-005: カード削除

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-004 |
| 関連 AC | AC-005-01, AC-005-02, AC-005-03 |
| 実装 | `src/petatto_kanban/app.py`, `models.py`, `display/settings_actions.py`, `display/settings_dialog_panels.py` |
| UI 契約 | [UC-003 §削除](./08-ui-behavior-contract.md#uc-003-カードコンポーネント), [UC-006 §システムタブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ) |

**説明**  
カードを **右クリックして離した** ときに削除する。設定により確認ダイアログを表示するか省略する。コンテキストメニューは表示しない。

**制約**
- `<ButtonRelease-3>`（右ボタン離し）で削除処理を開始（メニューなし）
- 押下のみ（`<Button-3>`）では削除しない
- `confirm_delete` が `true` のとき、削除前に確認ダイアログを表示
- `confirm_delete` が `false` のとき、即時削除
- 削除後 `board.json` を保存
- 設定ダイアログ「システム」タブの **「全てのカードを削除」** で一括削除可能（UC-006）。この操作は `confirm_delete` に関係なく **常に確認ダイアログ** を表示

---

### FR-010: カード位置ドラッグ

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-012 |
| 関連 AC | AC-010-01 |
| 実装 | `src/petatto_kanban/app.py` |

**説明**  
カードを左クリックドラッグで画面上の任意位置へ移動する。

**制約**
- カード枠・タイトル・期限パネル・進捗バーから左クリックドラッグで移動可能（[UC-003](./08-ui-behavior-contract.md#uc-003-カードコンポーネント)）
- ドラッグ中はカードの `x`, `y` を更新
- ドラッグ終了時に `board.json` を自動保存

---

### FR-025: カード進捗率

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-014 |
| 関連 AC | AC-025-01, AC-025-02 |
| 実装 | `src/petatto_kanban/app.py`, `src/petatto_kanban/progress.py` |

**説明**  
各カードに 0〜100% の進捗率を表示し、ホバー中のマウスホイールで ±10% ずつ変更する。

**制約**
- 進捗率は整数 0〜100 にクランプ
- バーは左から進捗率に比例して塗りつぶす
- 色は 0% 付近が赤、50% 付近が黄、100% 付近が緑（線形補間）
- バー中央に `NN%` を表示
- カード上にマウスホバー中: スクロールアップで +10%、スクロールダウンで −10%
- 進捗バー上でも左クリックドラッグでカード移動、右クリック離しで削除（FR-005, FR-010）
- 変更直後に `board.json` へ保存
- 新規カードの既定進捗率は `0`

---

### FR-014: カード期限

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-015 |
| 関連 AC | AC-014-01, AC-014-02, AC-014-03, AC-014-04 |
| 実装 | `src/petatto_kanban/app.py`, `due_date.py`, `due_date_picker.py`, `card_ui.py` |

**説明**  
カードに期限（日付）を設定・表示する。既定は期限なし。

**制約**
- 期限パネルに `期限なし` または `YYYY/MM/DD` を表示
- 期限当日はパネル背景を黄色系、期限超過は赤色系で強調
- 期限パネルで **クリック→離す→クリック→離す**（2回目の `<ButtonRelease-1>`）でカード外のフロート期限編集パネルを開く（別ウィンドウは使用しない）
- 編集パネル表示中に同一カードの期限パネルを **1回** クリック→離すとキャンセル（変更を保存しない）
- フロートパネルに月間カレンダーと「期限なし」ボタンを提供
- カレンダー上の **当日** 日付ボタンは緑色で表示
- パネル外（カード・メニューパネル・透過領域など）をクリックした場合は「閉じる」と同様にキャンセル（変更を保存しない）
- 日付選択または「期限なし」確定時に `board.json` へ保存

---

### FR-006: カード列間移動（M2）

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | deferred |
| 関連 US | US-005 |
| 関連 AC | AC-006-01 |
| 実装 | （M2 — 3 列カンバン再導入時） |

**説明**  
コンボボックスで移動先列を選択し、カードを別列へ移動する。（M1 では列 UI なし）

**制約**
- 移動元列は選択肢から除外
- 移動先列の末尾に追加
- 両列の order を再採番

**注記**  
列間ドラッグ＆ドロップによる移動は FR-006（M2）で提供。画面上の自由配置ドラッグは FR-010（M1）。

---

### FR-007: データ永続化

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | verified |
| 関連 US | US-006 |
| 関連 AC | AC-007-01, AC-007-02, AC-007-03 |
| 実装 | `src/petatto_kanban/storage.py` |
| データ契約 | [DC-001](./07-data-contract.md#dc-001-boardjson-スキーマ) |

**説明**  
ボードデータを JSON ファイルに保存し、次回起動時に復元する。

**制約**
- 保存先: `%USERPROFILE%\.petatto-kanban\board.json`
- ファイル不存在時はデフォルトボードを生成
- アプリ終了時に自動保存

---

### FR-008: 手動保存

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | deferred |
| 関連 US | US-006 |
| 関連 AC | AC-008-01 |
| 実装 | （M2） |

**説明**  
M1 では編集・ドラッグ・削除・終了時に自動保存するため、手動保存ボタンは提供しない。

---

### FR-009: 再読み込み

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | deferred |
| 関連 US | US-006 |
| 関連 AC | AC-009-01 |
| 実装 | （M2） |

**説明**  
M1 では再読み込みボタンは提供しない。次回起動時に `board.json` を読み込む。

---

### FR-020: オーバーレイモード

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-010 |
| 関連 AC | AC-020-01, AC-020-02 |
| 実装 | `src/petatto_kanban/display/overlay.py`, `app.py` |
| UI 契約 | [12-display-modes.md §6](./12-display-modes.md#6-オーバーレイモードoverlay-mode) |

**説明**  
指定ディスプレイを全画面表示。**オーバーレイモードはデスクトップモードと UI・透過・操作が同一** で、**常に最前面**（Always on Top）に表示する。

**制約**
- **M1 起動時の既定表示モード**（`settings.json` の `mode` 既定値 `"overlay"`）
- カードとメニューパネルのみ不透明、それ以外は透過
- 設定ダイアログ（UC-006）でデスクトップモードと切り替え可能（FR-022）
- Windows 11 以降で Win32 API により最前面・クリック透過を設定

---

### FR-021: ディスプレイ指定

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-010 |
| 関連 AC | AC-021-01 |
| 実装 | `src/petatto_kanban/display/monitors.py`, `app.py` |
| データ契約 | [DC-003](./07-data-contract.md#dc-003-表示設定スキーマ) |

**説明**  
**設定ダイアログ** から表示先モニターを選択し、`settings.json` に保存する。変更確定後、現在の表示モード（オーバーレイ / デスクトップ）に応じて指定ディスプレイへ全画面再配置する。

**制約**
- メニューパネルにはディスプレイ選択 UI を置かない（M1）
- 選択肢は OS が認識するモニター一覧

---

### FR-024: 削除確認設定

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-013 |
| 関連 AC | AC-024-01 |
| 実装 | `src/petatto_kanban/display/settings_dialog.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `display/settings.py`, `app.py` |
| UI 契約 | [UC-006 §システムタブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ) |

**説明**  
設定ダイアログ **「システム」タブ** で「カード削除時に確認ダイアログを表示する」を ON/OFF できる。

**制約**
- 既定値: `true`（確認あり）
- `settings.json` の `confirm_delete` に永続化

---

### FR-019: デスクトップモード

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | implemented |
| 関連 US | US-009 |
| 関連 AC | AC-019-01, AC-019-02 |
| 実装 | `src/petatto_kanban/display/desktop.py`, `display/transparent.py`, `display/modes.py`, `display/menu_panel_host.py`, `display/desktop_board_controller.py`, `display/foreground.py` |
| UI 契約 | [12-display-modes.md §5](./12-display-modes.md#5-デスクトップモードdesktop-mode) |

**説明**  
指定ディスプレイを全画面表示。**オーバーレイモードと基本的に同一**（透過・全画面・カンバン UI）だが、**カード等は通常ウィンドウ（ブラウザ等）より背面**に固定する。**メニューパネルだけは常に最前面**とし、＋・設定・終了をいつでも操作可能にする。

**Z オーダー（下 → 上）:** デスクトップ（壁紙）→ **Petatto-Kanban 本体（カード等）** → 他のウィンドウ → **メニューパネル**

**制約**
- オーバーレイモードと共通の透過・クリック透過・ディスプレイ指定（[12-display-modes.md §2](./12-display-modes.md#2-モード比較)）
- 設定ダイアログ（UC-006）でオーバーレイモードと相互切替（FR-022）
- `settings.json` の `mode: "desktop"` で永続化
- 本体は `display/desktop.py`（Z オーダー `HWND_BOTTOM` 等）。メニューは `display/menu_panel_host.py`（独立 Toplevel + `-topmost`）
- 昇格・降格ロジックは `display/desktop_board_controller.py`（DM-DESKTOP-02 / 03）。他アプリ判定は `display/foreground.py`
- Windows 11 以降

---

### FR-023: アプリ終了

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-011 |
| 関連 AC | AC-023-01, AC-023-02 |
| 実装 | `src/petatto_kanban/app.py`, `display/settings_actions.py` |
| UI 契約 | [UC-002](./08-ui-behavior-contract.md#uc-002-メニューパネル) |

**説明**  
メニューパネルホバー時の **×ボタン** をクリックして離す（`<ButtonRelease-1>`）とアプリを終了する。終了前にボード・表示設定を自動保存する。

**制約**
- オーバーレイモード（タイトルバーなし）でも終了できること
- `WM_DELETE_WINDOW` と同じ `_on_close` 処理を呼ぶ
- 設定ダイアログ「システム」タブの `confirm_exit` が `true` のとき、終了前に確認ダイアログを表示（キャンセル時は終了しない）
- `confirm_exit` 既定値は `false`（即時終了）

---

## M2 — 表示モード拡張

### FR-018: ウィンドウモード

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | deferred |
| 関連 US | US-008 |
| 関連 AC | AC-018-01 |
| UI 契約 | [12-display-modes.md §4](./12-display-modes.md#4-ウィンドウモードwindow-mode) |

**説明**  
通常の OS ウィンドウとしてカンバンを表示する。タイトルバー・リサイズ・不透明背景。

**制約**
- 最小サイズ 960 × 540 px

---

### FR-022: 表示モード切替

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | implemented |
| 関連 US | US-008, US-009, US-010 |
| 関連 AC | AC-022-01, AC-022-02 |
| 実装 | `src/petatto_kanban/display/settings_dialog.py`, `display/settings_dialog_panels.py`, `display/modes.py`, `app.py` |
| UI 契約 | [UC-006 §表示タブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ) |

**説明**  
**M1 拡張:** 設定ダイアログ **「表示」タブ** から **オーバーレイモード** と **デスクトップモード** を実行中に切り替える。  
**M2:** ウィンドウモードを追加し 3 モード切替を完成させる。

**制約（M1 拡張）**
- 切替 UI は設定ダイアログ「表示」タブ（メニューパネル ⚙ から開く）
- OK 確定で `settings.json` の `mode` を保存し、即時再描画
- ボードデータ・カード座標は保持

---

### FR-026: UI サイズ設定

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-016 |
| 関連 AC | AC-026-01, AC-026-02, AC-026-03, AC-026-04 |
| 実装 | `src/petatto_kanban/display/ui_scale.py`, `display/ui_scale_labels.py`, `display/card_layout.py`, `display/ui_metrics.py`, `display/ui_chrome.py`, `card_renderer.py`, `display/settings.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `app.py`, `menu_panel_layout.py`, `menu_panel.py`, `due_date_picker.py` |
| UI 契約 | [UC-006 §表示タブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ), [UC-009 §UI スケール](./08-ui-behavior-contract.md#uc-009-ui-スケール) |

**説明**  
設定ダイアログ **「表示」タブ** で UI 全体の表示サイズ（**小 / 標準 / 大 / 極大**）を選択できる。カード・メニューパネル・期限パネル等のフォントとレイアウト寸法を一括でスケールする。

**制約**
- 選択肢: **小**（`small`）/ **標準**（`medium`）/ **大**（`large`）/ **極大**（`xlarge`、標準の 1.25 倍）。既定値は **標準**
- `settings.json` の `ui_size` に永続化し、次回起動時に復元
- OK 確定後、表示モードの切替を伴わない場合でも **即時再描画**（カード・メニューパネルを再構築）
- カードの `x` / `y` 座標（`board.json`）は **変更しない**（見た目のサイズのみ変化）
- 不明・欠損・不正な `ui_size` は **標準** として読み込む
- スケール係数と基準寸法は [UC-009](./08-ui-behavior-contract.md#uc-009-ui-スケール) に従う

---

### FR-027: UI フォント設定

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-017 |
| 関連 AC | AC-027-01, AC-027-02, AC-027-03 |
| 実装 | `src/petatto_kanban/display/ui_font.py`, `display/ui_font_labels.py`, `display/ui_metrics.py`, `display/settings.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `display/ui_chrome.py`, `card_renderer.py`, `app.py` |
| UI 契約 | [UC-006 §表示タブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ), [UC-010 §UI フォント](./08-ui-behavior-contract.md#uc-010-ui-フォント) |

**説明**  
設定ダイアログ **「表示」タブ** でアプリ全体の **フォントファミリー** を選択できる。カード・メニューパネル・期限パネル等のテキスト描画に共通適用する。**フォントサイズ** は FR-026（UI サイズ）が担当し、本要件はファミリー変更のみを扱う。

**制約**
- 選択肢（M1）: **Segoe UI** / **メイリオ** / **游ゴシック** / **MS ゴシック**（Windows 11 標準搭載を前提）
- `settings.json` の `ui_font` に永続化。既定値は **Segoe UI**（`segoe_ui`）
- OK 確定後、表示モード・ディスプレイ・UI サイズを変えずに **即時再描画**（FR-026 と同様にカード・メニューパネルを再構築）
- カードの `x` / `y` 座標は **変更しない**
- 不明・欠損・不正な `ui_font` は **Segoe UI** として読み込む
- tkinter フォント名への対応は [UC-010](./08-ui-behavior-contract.md#uc-010-ui-フォント) に従う
- OS にフォントが存在しない場合は **Segoe UI** にフォールバック（起動時・適用時）

---

### FR-028: UI カラーテーマ設定

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-018 |
| 関連 AC | AC-028-01, AC-028-02, AC-028-03 |
| 実装 | `src/petatto_kanban/display/ui_theme.py`, `display/ui_theme_labels.py`, `display/settings.py`, `display/settings_dialog_tabs.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `display/ui_chrome.py`, `card_renderer.py`, `menu_panel.py`, `due_date_picker.py`, `app.py` |
| UI 契約 | [UC-006 §テーマタブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ), [UC-011 §UI カラーテーマ](./08-ui-behavior-contract.md#uc-011-ui-カラーテーマ) |

**説明**  
設定ダイアログ **「テーマ」タブ** でアプリ全体の **カラーテーマ**（背景色・文字色のプリセット）を選択できる。カード枠・タイトル・メニューパネル・期限編集パネルの枠・設定ダイアログ等に反映する。**期限の意味色**（当日の黄・超過の赤）と **進捗バーの塗り色** はテーマの影響を受けない（可読性・状態識別のため固定）。

**制約**
- 選択肢（M1）: **10 種** — `default` / `dark` / `sandy` / `forest` / `fancy` / `ocean` / `sunset` / `slate` / `rose` / `midnight`（[UC-011](./08-ui-behavior-contract.md#uc-011-ui-カラーテーマ) のパレット表）
- `settings.json` の `ui_theme` に永続化。既定値は **default**（現行配色）
- OK 確定後、表示モード・ディスプレイ・UI サイズ・フォントを変えずに **即時再描画**（FR-026 / FR-027 と同様）
- カードの `x` / `y` 座標は **変更しない**
- 不明・欠損・不正な `ui_theme` は **default** として読み込む
- 各テーマの背景色・文字色は **コントラスト比 4.5:1 以上**（通常テキスト）を目標に選定する（[UC-011](./08-ui-behavior-contract.md#uc-011-ui-カラーテーマ)）
- オーバーレイ透過色（`TRANSPARENT_COLOR`）・Win32 透過処理はテーマ対象外

---

### FR-029: Windows ログオン時自動起動

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | implemented |
| 関連 US | US-019 |
| 関連 AC | AC-029-01, AC-029-02, AC-029-03, AC-029-05, AC-029-06 |
| 実装 | `src/petatto_kanban/system/auto_start.py`, `system/launch_command.py`, `display/settings.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `app.py` |
| UI 契約 | [UC-006 §システムタブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ) |

**説明**  
設定ダイアログ **「システム」タブ** で、Windows ログオン時に Petatto-Kanban を自動起動するかを切り替えられる。

**制約**
- **対象 OS は Windows 11 以降のみ**（NFR-011）。macOS / Linux はスコープ外で、動作・UI・受け入れ基準を定義しない
- `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` に登録する。キーが無ければ作成する
- `settings.json` の `launch_at_login`（boolean）に永続化。既定値 **false**
- OK 確定時にレジストリへ反映。反映失敗時はエラーメッセージを表示し、**ダイアログで変更した全項目をメモリ上もロールバック**して **`settings.json` は更新しない**（「設定を保存しました」は出さない）
- アプリ起動時、`launch_at_login` が `true` のときだけコマンド行を **再書き込み**（`.exe` 更新後のパスずれ対策）。`false` のときはレジストリを変更しない（削除は設定ダイアログで OFF にしたときのみ）
- PyInstaller ビルド（`sys.frozen`）では **`Petatto-Kanban.exe` の絶対パス** を登録
- 開発起動では `python.exe` と同じディレクトリの `pythonw.exe`（存在時）+ `-m petatto_kanban` を登録。`pythonw.exe` が無ければ `sys.executable` を使う
- レジストリ値名: **`Petatto-Kanban`**
- 起動コマンド解決は `system/launch_command.py`、レジストリ I/O は `system/auto_start.py` に分離する

---

### FR-030: キーボードショートカットで新規カード作成

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | implemented |
| 関連 US | US-020 |
| 関連 AC | AC-030-01, AC-030-02, AC-030-03, AC-030-04, AC-030-05 |
| 実装 | `system/shortcut.py`, `system/hotkey.py`, `system/hotkey_pump.py`, `display/settings.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `app.py` |
| UI 契約 | [UC-006 §操作タブ](./08-ui-behavior-contract.md#uc-006-設定ダイアログ), [UC-012](./08-ui-behavior-contract.md#uc-012-キーボードショートカット) |
| データ契約 | [DC-003 `shortcuts`](./07-data-contract.md#dc-003-表示設定スキーマ) |

**説明**  
キーボードショートカットで [FR-003](#fr-003-カード作成) と同じ新規カード作成を行う。既定は **Ctrl+Shift+N**。割り当ては設定ダイアログ **「操作」タブ** で変更できる。

**制約**
- **対象 OS は Windows 11 以降のみ**（NFR-011）
- **グローバルホットキー**（Win32 `RegisterHotKey`）。アプリ起動中は他アプリが前面でも発火する（オーバーレイのクリック透過でもメニューにフォーカスしなくてよい）
- 既定コード: **`Ctrl+Shift+N`**（`settings.json` の `shortcuts.new_card`）
- 作成結果は FR-003 / [UC-004](./08-ui-behavior-contract.md#uc-004-カード即時追加) と同一（配置・初期タイトル・インライン編集・`board.json` 保存）
- 発火時、進行中のタイトルインライン編集は **確定**し、期限パネルが開いていれば **キャンセル**してからカードを追加する
- **設定ダイアログ表示中は発火しない**（カードをダイアログの裏に作らない）
- コード形式: `Ctrl` / `Alt` / `Shift` の 1 つ以上 + 英数字 1 キーまたは F1〜F12。正規化は `Ctrl+Alt+Shift+N` の順。Windows キーは対象外
- 修飾キーのみ、または修飾なしの単一キーは割り当て不可
- 欠損・空・不正な `shortcuts.new_card` は既定 `Ctrl+Shift+N` にフォールバック
- コード正規化は `system/shortcut.py`、セッションは `system/hotkey.py`、Win32 メッセージポンプは `system/hotkey_pump.py` に分離する
- `WM_HOTKEY` は **専用スレッド** のメッセージ専用ウィンドウで受信する。WndProc はネイティブ `DefWindowProcW` のみとし、Python ctypes コールバックは使わない。Tk スレッドは `after` でキューを `poll()` する
- OK 確定時にホットキーを再登録。`RegisterHotKey` 失敗時はエラーを表示し、**ダイアログ全項目をロールバック**して `settings.json` は更新しない（FR-029 の失敗時と同様）
- アプリ終了時にホットキーを解除する

---

### FR-031: ローカルエラーログ

| 属性 | 値 |
|------|-----|
| 優先度 | Must |
| ステータス | implemented |
| 関連 US | US-021 |
| 関連 AC | AC-031-01, AC-031-02, AC-031-03 |
| 実装 | `system/error_log.py`、起動時に `app.py` から初期化 |
| データ契約 | [DC-004](./07-data-contract.md#dc-004-エラーログ) |

**説明**  
アプリ起動中に発生したエラー（未捕捉例外・Tk コールバック例外・`logging` の ERROR 以上）を、ユーザー PC 上のログディレクトリへ書き出す。診断・再現に使う。既定で有効（オプトアウトしない）。

**制約**
- 保存先: `%USERPROFILE%\.petatto-kanban\logs\`（ディレクトリが無ければ作成する）
- ファイル名: `petatto-kanban-YYYY-MM-DD.log`（ローカル日付、1 日 1 ファイル）
- エンコーディング UTF-8。追記モード。保持は直近 14 日分。それより古いファイルは起動時に削除してよい
- 標準ライブラリの `logging` のみ（NFR-005）。`print` デバッグは使わない
- 捕捉対象: `sys.excepthook`、tkinter `report_callback_exception`、専用スレッド（ホットキーポンプ等）の未捕捉例外、アプリ内 `logger.error` / `logger.exception`
- 1 レコードに含める: 時刻（ISO 8601）、ログレベル、ロガー名、メッセージ、スタックトレース（ある場合）、アプリバージョン、Python バージョン、OS 概要
- **カードタイトル・ボード内容・認証情報・環境変数の秘密は書かない**。ユーザーホームパスは `~` に置換してよい
- ログ書き込み失敗（ディスク満杯・権限など）でも **アプリは継続**する。ユーザー向けダイアログは出さない
- ログ I/O は UI を止めない。書き込み失敗はプロセス内で繰り返して騒がない
- 本要件はオフライン完結。ネットワークは使わない

---

### FR-032: GitHub Issue 任意起票

| 属性 | 値 |
|------|-----|
| 優先度 | Should |
| ステータス | cancelled |
| 関連 US | — |
| 関連 AC | — |
| 実装 | なし |

**説明**  
アプリから GitHub Issue を自動起票する機能。**採用しない。**

GitHub REST API で Issue を作成するには認証トークンが必要で、リポジトリで Issues を全員に許可していても同じである。利用者に PAT を求めたり、exe にトークンを埋め込んだりはしない。診断は [FR-031](#fr-031-ローカルエラーログ) のローカルログのみとする。

---

## M2 以降（その他）

| ID | 機能 | マイルストーン |
|----|------|----------------|
| FR-011 | 複数ボードの作成・切り替え | M2 |
| FR-012 | 列の追加・削除・名称変更・並び替え（3 列カンバン） | M2 |
| FR-013 | カードへの色付きラベル付与 | M2 |
| FR-015 | キーワード・ラベルによる検索・フィルタ | M2 |
| FR-016 | 列ごとの WIP 上限 | M3 |
| FR-017 | ユーザー認証・クラウド同期 | M3 |
