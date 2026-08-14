# 08 — UI 操作契約

| 項目 | 内容 |
|------|------|
| ステータス | Active |
| 実装 | `src/petatto_kanban/app.py`, `menu_panel.py`, `new_card_placement.py` |

---

## UC-001: オーバーレイ / デスクトップ メイン画面

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-001, FR-019, FR-020 |
| 関連 AC | AC-001-01, AC-019-01, AC-019-02, AC-020-01, AC-020-02 |
| 表示モード | [12-display-modes.md](./12-display-modes.md) |

| 要素 | 仕様 |
|------|------|
| 表示領域 | 指定ディスプレイ全画面 |
| 背景 | 透過（`-transparentcolor` + Win32 レイヤードウィンドウ） |
| Z オーダー | 最前面 |
| 終了時 | データ自動保存（FR-007） |
| テーマ | Windows 環境で `vista` が利用可能なら適用 |

```
[ ディスプレイ全体 — 最前面・透過 ]
┌─────────────────────────────────────────────────────────┐
│ ░░ 下のアプリが透過で見える ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│   ┌──────────┐                              ○< │
│   │ Card     │      ホバー → ○＋○⚙○×○< │
│   │ ┌title──┐│                    メニューパネル │
│   │ │ title ││                                          │
│   │ └───────┘│                                          │
│   └──────────┘                                          │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────────────────────────┘
  ↑ カードとメニューパネルのみ不透明。それ以外はクリック透過
```

---

## UC-002: メニューパネル

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-003, FR-019, FR-023 |
| 実装 | `src/petatto_kanban/menu_panel.py`, `menu_panel_layout.py`, `display/menu_panel_host.py`, `app.py` |
| UI 契約 | 旧「ツールバー」をメニューパネルに置換（M1） |

### 概要

画面右上（デフォルト）に **円形 `<`** のみ表示するコンパクトな操作入口。ホバーで左へ **＋・⚙・×** の円形ボタンを展開する。フレーム背景は透過し、円形ボタンのみ不透明。

### 定数（`menu_panel_layout.py` / `menu_panel.py`）

| 定数 | 値 | 説明 |
|------|-----|------|
| `MENU_CIRCLE_SIZE` | 36 | 各円ボタンの一辺（px）。[UC-009](./08-ui-behavior-contract.md#uc-009-ui-スケール) でスケール |
| `MENU_DEFAULT_MARGIN_X/Y` | 16 | 画面端からのデフォルト余白 |
| `MENU_HOVER_HIDE_DELAY_MS` | 120 | ホバー解除後に収納するまでの遅延 |
| `MENU_ACTION_LABELS` | ＋, ⚙, × | 展開ボタン（左→右） |

### 操作

| 要素 | 操作 | 結果 |
|------|------|------|
| 円形 `<` | — | 通常時は **`<` のみ** 表示 |
| メニューパネル | マウスホバー | 左へ **＋**・**⚙**・**×** を展開（`<` 右端は固定） |
| **＋** | クリック→離す | `<ButtonRelease-1>`。UC-004 カード即時追加 |
| **⚙** | クリック→離す | `<ButtonRelease-1>`。設定ダイアログ |
| **×** | クリック→離す | `<ButtonRelease-1>`。`_on_close()` |
| **`<`** | 左クリックドラッグ | 位置変更。`menu_panel_x/y` を `settings.json` へ保存 |

### クリックの反応タイミング

- **＋**・**⚙**・**×** は `<Button-1>` 押下のみでは動作しない。**離した** とき（`<ButtonRelease-1>`）に処理する
- 押下と離しが **同一ボタン上** の場合のみ有効

### レイアウト・配置

- **ホバー時（左→右）:** `○＋` `○⚙` `○×` `○<` — ボタン間・`×` と `<` 間に隙間なし
- **展開方向:** 左方向。`<` 円の屏幕位置は展開・収納で不変（`place(anchor=NE)`）
- **背景:** `TRANSPARENT_COLOR`。操作ボタン Canvas と `<` 円のみクリック可能
- **ホバー維持:** 子ウィジェット間の Enter/Leave を深度カウント。操作ボタンは単一 Canvas に描画
- **デフォルト位置:** 画面右上（右端・上端とも 16px マージン）

### デスクトップモードでの Z オーダー（DM-DESKTOP-01）

- メニューパネルは **独立した透過 Toplevel**（`display/menu_panel_host.py`）上に描画する
- デスクトップモードでは Toplevel に `-topmost` を付与し、**他アプリより常に前面**に表示する
- **メニューアクティブ時**（ホバー・フォーカス・押下）は `DesktopBoardController.activate_from_menu()` で **全カードを含む本体** を一時最前面に出す（DM-DESKTOP-02）
- **他アプリアクティブ時**は `DesktopBoardController.lower_on_foreign_app_active()` で本体を即時背面へ（DM-DESKTOP-03）
- カード等は本体ウィンドウ（背面）に残る。メニューのホバー・ドラッグ・永続化はオーバーレイ時と同一

### 永続化

| フィールド | 説明 |
|------------|------|
| `menu_panel_x` | 保存時点のパネル左上 X（展開/収納状態に依存） |
| `menu_panel_y` | パネル左上 Y |

未設定時は `_place_menu_panel()` がデフォルト位置を計算する。

---

## UC-003: カードコンポーネント

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-002, FR-003, FR-004, FR-005, FR-010, FR-025, FR-014, FR-026, FR-028 |
| 関連 AC | AC-002-01, AC-002-02 |
| 実装 | `card_renderer.py`, `display/card_layout.py`, `display/card_frame.py`, `card_ui.py`, `app.py` |

| 要素 | 操作 | 結果 |
|------|------|------|
| カード枠 | 左クリックドラッグ | 画面上の位置を変更（FR-010） |
| カード枠 | 右クリック離し | **削除処理**（FR-005）。メニューは表示しない |
| タイトル | 左クリックドラッグ | 画面上の位置を変更（FR-010） |
| タイトル | 右クリック離し | **削除処理**（FR-005）。メニューは表示しない |
| タイトル | クリック→離す→クリック→離す | インライン編集（UC-005）。2回目の離しで開始 |
| タイトル | — | 太字、`wraplength=155`（標準時）。`GROOVE` 枠の内側フレームで表示 |
| 進捗バー | ホバー中スクロールアップ | 進捗率 +10%（最大 100%）（FR-025） |
| 進捗バー | ホバー中スクロールダウン | 進捗率 −10%（最小 0%）（FR-025） |
| 進捗バー | 左クリックドラッグ | 画面上の位置を変更（FR-010） |
| 進捗バー | 右クリック離し | **削除処理**（FR-005） |
| 進捗バー | — | 左から塗りつぶし。0%≈赤 / 50%≈黄 / 100%≈緑（**塗り色はテーマ非適用**）。中央に `NN%` 表示。トラック背景はテーマ適用 |
| 期限パネル | 左クリックドラッグ | 画面上の位置を変更（FR-010） |
| 期限パネル | 右クリック離し | **削除処理**（FR-005） |
| 期限パネル | クリック→離す→クリック→離す | 期限編集パネル（UC-008）。2回目の離しで表示 |
| 期限パネル | — | `期限なし` または `YYYY/MM/DD`。当日=黄 / 超過=赤（**テーマ非適用** — [UC-011](./08-ui-behavior-contract.md#uc-011-ui-カラーテーマ)） |

**削除**
- 右ボタンを **離した** とき（`<ButtonRelease-3>`）→ `_delete_card()` を呼び出し
- 右ボタン **押下のみ** では削除しない
- `confirm_delete=true` 時: 確認ダイアログ → 削除
- `confirm_delete=false` 時: 即時削除

**配置・サイズ**
- `place(x, y)` — 座標は `board.json` に永続化
- 最小サイズ・フォント・進捗バー高さ等は [UC-009](./08-ui-behavior-contract.md#uc-009-ui-スケール) のスケール後寸法を用いる（標準時: `CARD_MIN_WIDTH = 175`、`CARD_MIN_HEIGHT = 108`、横長黄金比 φ、フォント 10pt）
- 実際の枠サイズ: **幅**は `CARD_MIN_WIDTH` に固定（`winfo_reqwidth` では拡張しない）。**高さ**は `CARD_MIN_HEIGHT` を下限とし、タイトルの改行・`wraplength` 折り返しで内容が増えたときは縦方向のみ拡張する（期限・進捗を隠さない）

---

## UC-004: カード即時追加

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-003, FR-030 |
| 関連 AC | AC-003-01, AC-003-02, AC-030-01 |
| 実装 | `src/petatto_kanban/app.py`, `new_card_placement.py`, `menu_panel.py` |

| 属性 | 値 |
|------|-----|
| トリガー | メニューパネルホバー時の **＋** ボタンをクリックして離す（`<ButtonRelease-1>`）、または [UC-012](#uc-012-キーボードショートカット) の新規カードショートカット |
| 初期タイトル | `新しいタスク`（`DEFAULT_NEW_CARD_TITLE` — `new_card_placement.py`） |
| 保存 | 追加直後に `board.json` へ永続化 |
| タイトル編集 | 追加直後に UC-005 のインライン編集を自動開始（全選択・フォーカス） |

### 配置（メニューパネル直下・右端揃え）

座標は `new_card_placement.compute_new_card_position()` で算出する。入力は `MenuPanel.bounds()`（`menu_panel_layout.MenuPanelRect`）とカード幅。

| 定数 | 値 | 説明 |
|------|-----|------|
| `DEFAULT_NEW_CARD_GAP_Y` | 2 | パネル下端からカード上端までの余白（px） |
| `DEFAULT_NEW_CARD_INSET_X` | 128 | 右端揃え位置からさらに左へ寄せる量（px） |
| `DEFAULT_NEW_CARD_STACK_OFFSET_X/Y` | 12 | 連続追加ごとに左・下へずらす量（px） |
| カード幅 | `CARD_MIN_WIDTH + 2 * CARD_FRAME_BORDER`（177） | 枠線込みの配置基準幅 |
| 画面内クランプ | `clamp_card_position_to_monitor()` | 算出後にモニター範囲内へ収める |

| 項目 | 式 |
|------|-----|
| 1 枚目の X | `panel.right - card_width - inset_x`（`panel.right` は NE アンカー） |
| 1 枚目の Y | `panel.bottom + gap_y`（パネル直下） |
| N 枚目（0 始まり） | 左へ `N * 12px`、下へ `N * 12px` |
| クランプ | `0 <= x <= monitor_width - card_width`、`0 <= y <= monitor_height - card_height` |

**注意:** `panel.right` は展開/収納に関わらず `<` 円の右端（NE アンカー）を使う。幅の取得が未確定のときも `_content_width()` で展開状態を反映する。

---

## UC-012: キーボードショートカット

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-030, FR-003 |
| 関連 AC | AC-030-01, AC-030-02, AC-030-03, AC-030-04, AC-030-05 |
| 実装 | `system/shortcut.py`, `system/hotkey.py`, `system/hotkey_pump.py`, `app.py` |
| 設定 UI | [UC-006 §操作タブ](#uc-006-設定ダイアログ) |

| 項目 | 仕様 |
|------|------|
| 方式 | Windows グローバルホットキー（`RegisterHotKey`）。受信は Tk とは別スレッド（`hotkey_pump.py`）のメッセージ専用ウィンドウ（ネイティブ `DefWindowProc`）。アプリが起動していれば他ウィンドウ前面でも発火 |
| 対象 OS | Windows 11 以降 |
| 既定 | 新規カード作成 = `Ctrl+Shift+N` |
| 動作 | 発火時は [UC-004](#uc-004-カード即時追加) と同一（配置・初期タイトル・インライン編集・保存） |
| 編集中 | タイトルインライン編集中なら確定。期限パネルが開いていればキャンセル。その後にカード追加 |
| 抑制 | 設定ダイアログ表示中は発火しない |
| 再登録 | 設定 OK 成功後。失敗時はダイアログ全項目をロールバックし、旧コードのまま |
| 解除 | アプリ終了時 |

M1 で割り当て可能なアクションは **新規カード作成** のみ。他アクションは将来の操作タブ拡張とする。

---

## UC-005: タイトルインライン編集

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-004 |
| 関連 AC | AC-004-01, AC-004-02 |

| 属性 | 値 |
|------|-----|
| トリガー | タイトルで `<Button-1>` → `<ButtonRelease-1>` を2回（**2回目の離し**で開始）、または FR-003 によるカード追加直後 |
| UI | 同一カード枠内の `Entry` に切り替え |
| 入力 | タイトル（必須） |
| 確定 | Enter、フォーカスアウト、同一カードのタイトル以外をクリック、またはカード追加・設定・終了時 |
| キャンセル | Escape |

---

## UC-008: 期限編集パネル

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-014 |
| 関連 AC | AC-014-01, AC-014-02, AC-014-03, AC-014-04 |

| 属性 | 値 |
|------|-----|
| トリガー | 期限パネルで `<Button-1>` → `<ButtonRelease-1>` を2回（**2回目の離し**で表示） |
| 閉じる（同一カード） | 編集中に期限パネルを1回クリック→離す、または「閉じる」/ Escape / パネル外クリック |
| UI | カード外のフロートパネル（`DueDatePicker` — 別ウィンドウではない） |
| 配置 | 期限パネル直下（画面端では上側へ自動調整） |
| カレンダー | 月間表示。日付クリックで確定。**当日の日付ボタンは緑色** |
| 期限なし | 「期限なし」ボタンで `due_date = null` |
| 閉じる | 「閉じる」ボタン、Escape、またはパネル外クリックでキャンセル |
| 保存 | 日付選択・期限なし確定時に `board.json` へ永続化 |

---

## UC-006: 設定ダイアログ

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-003, FR-005, FR-019, FR-023, FR-024, FR-026, FR-027, FR-028, FR-029, FR-030, FR-032 |
| 実装 | `src/petatto_kanban/display/settings_dialog.py`, `settings_dialog_tabs.py`, `settings_dialog_labels.py`, `settings_dialog_panels.py`, `settings_actions.py`, `mode_labels.py`, `system/auto_start.py`, `system/launch_command.py`, `system/shortcut.py`, `system/hotkey.py`, `system/hotkey_pump.py`, `app.py`（FR-032 のトークン警告は実装時に `settings_actions` へ追加） |
| 関連 AC | AC-005-03, AC-019-01, AC-021-01, AC-022-02, AC-023-02, AC-024-01, AC-029-01, AC-029-02, AC-029-06, AC-030-02, AC-030-03, AC-030-04, AC-030-05, AC-032-05, AC-032-06, AC-032-07 |

### タブ構成

| タブ | ID（実装定数） | 関連 FR | 項目 |
|------|----------------|---------|------|
| **表示** | `SETTINGS_TAB_DISPLAY` | FR-019, FR-020, FR-021, FR-022, FR-026, FR-027 | 表示モード、表示ディスプレイ、UI サイズ、**フォント** |
| **テーマ** | `SETTINGS_TAB_THEME` | FR-028 | **カラーテーマ** |
| **操作** | `SETTINGS_TAB_ACTIONS` | FR-030 | **ショートカットキー** |
| **システム** | `SETTINGS_TAB_SYSTEM` | FR-024, FR-023, FR-029, FR-005, FR-032 | 確認オプション、**自動起動**、**エラー報告**、**全カード削除** |

- UI は `ttk.Notebook` でタブ切り替え
- `settings_dialog_tabs.DISPLAY_TAB_FIELDS` に `ui_size`, `ui_font` を含む
- `settings_dialog_tabs.THEME_TAB_FIELDS` に `ui_theme` を含む
- `settings_dialog_tabs.ACTIONS_TAB_FIELDS` に `shortcut_new_card`（`shortcuts.new_card`）を含む
- `settings_dialog_tabs.SYSTEM_TAB_FIELDS` に `confirm_delete`, `confirm_exit`, `launch_at_login`, `report_errors_to_github` を含む
- OK で `settings.json` に `mode`, `monitor_index`, `confirm_delete`, `confirm_exit`, `launch_at_login`, `ui_size`, `ui_font`, `ui_theme`, `shortcuts`, `report_errors_to_github` を保存（タブに関係なく一括）
- キャンセル時は変更を破棄

### 表示タブ

| 要素 | 仕様 |
|------|------|
| **表示モード** | コンボボックス（`readonly`）: `オーバーレイ` / `デスクトップ` |
| **表示ディスプレイ** | コンボボックス（OS 認識モニター一覧、`readonly`） |
| **UI サイズ** | コンボボックス（`readonly`）: `小` / `標準` / `大` / `極大`（FR-026）。既定 **標準** |
| **フォント** | コンボボックス（`readonly`）: Segoe UI / メイリオ / 游ゴシック / MS ゴシック（FR-027）。既定 **Segoe UI** |

### テーマタブ

| 要素 | 仕様 |
|------|------|
| **カラーテーマ** | コンボボックス（`readonly`）: Default / ダーク / サンディ / フォレスト / ファンシー / オーシャン / サンセット / スレート / ローズ / ミッドナイト（FR-028）。既定 **Default** |

### 操作タブ

| 要素 | 仕様 |
|------|------|
| 行ラベル | 「新規カード作成」 |
| 割り当て表示 | 現在のコード（既定 `Ctrl+Shift+N`）を読み取り専用で表示 |
| **変更** | 押下後、次に入力したキーコンボを仮割り当て。Escape で変更キャンセル |
| **既定に戻す** | `Ctrl+Shift+N` に戻す |
| 入力規則 | 修飾（Ctrl / Alt / Shift）を 1 つ以上含む。単体キー・修飾のみは受け付けない |
| 確定 | OK でホットキーを再登録し `shortcuts.new_card` を保存。失敗時はダイアログ全項目をロールバックし `settings.json` を保存しない（FR-029 と同様） |

### システムタブ

| 要素 | 仕様 |
|------|------|
| チェックボックス | 「カード削除時に確認ダイアログを表示する」 |
| チェックボックス | 「アプリ終了時に確認ダイアログを表示する」（`confirm_exit`、既定 `false`） |
| チェックボックス | 「Windows ログオン時に自動起動する」（`launch_at_login`、既定 `false`、FR-029）。対象 OS は **Windows 11 以降** |
| チェックボックス | 「エラー時に GitHub Issue を自動起票する」（`report_errors_to_github`、既定 `false`、FR-032）。**起票するかどうかはこのチェックだけで切り替える** |
| エラー報告の初期表示 | ダイアログ表示時は `settings.json` の `report_errors_to_github` を反映する |
| エラー報告の確定 | OK で `report_errors_to_github` を保存し、**再起動せず**直後から ON/OFF を適用する。キャンセル時は破棄 |
| エラー報告の補足 | トークン入力欄は置かない。`%USERPROFILE%\.petatto-kanban\github_token` または環境変数 `PETATTO_GITHUB_TOKEN`。ON かつトークン無しで OK したときは警告 1 回（設定値は保存する） |
| 自動起動の確定 | OK 時に Run キーへ反映。失敗時はダイアログ全項目をロールバックし `settings.json` を保存しない。成功時のみ「設定を保存しました」 |
| ボタン | **「全てのカードを削除」** — 押下で確認ダイアログ（枚数表示）→ 全カード削除・`board.json` 保存・即時再描画。`confirm_delete` 設定に関係なく **常に確認** |

### 共通

| 項目 | 仕様 |
|------|------|
| モード変更時 | 指定ディスプレイ上でオーバーレイまたはデスクトップ表示に即時切替。カード・メニューパネルは保持 |
| ディスプレイ変更時 | 現在の表示モードのまま全画面を再配置し、カードを再描画 |
| UI サイズ変更時 | 表示モード・ディスプレイを変えずにカード・メニューパネルを再描画。カード座標は保持 |
| フォント変更時 | UI サイズ変更時と同様に即時再描画。カード座標は保持 |
| テーマ変更時 | フォント変更時と同様に即時再描画。カード座標は保持。[UC-011](./08-ui-behavior-contract.md#uc-011-ui-カラーテーマ) の適用・除外範囲に従う |
| GitHub 起票設定変更時 | OK 直後から `report_errors_to_github` を適用する。再描画は不要。OFF なら以降 HTTP しない |

---

## UC-009: UI スケール

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-026 |
| 関連 AC | AC-026-01, AC-026-02, AC-026-03 |
| 実装 | `src/petatto_kanban/display/ui_scale.py`, `display/ui_font.py`, `display/ui_metrics.py`, `app.py`, `menu_panel_layout.py`, `menu_panel.py`, `due_date_picker.py`, `card_renderer.py`, `display/ui_chrome.py` |

`ui_size`（FR-026）と `ui_font`（FR-027）を組み合わせて `UiMetrics` を生成する。**サイズ** は `ui_size` のスケール係数、**ファミリー名** は `ui_font` から決定する。

`ui_size` に応じて、以下の **基準値（標準 = scale 1.0）** にスケール係数を乗算する。各値は `round(基準 * scale)`（フォント pt は最小 8）とする。フォントタプルの第 1 要素（ファミリー）は [UC-010](./08-ui-behavior-contract.md#uc-010-ui-フォント) に従う。

| 定数 / 要素 | 基準値（medium） | 適用箇所 |
|-------------|------------------|----------|
| `CARD_MIN_WIDTH` | 175 px | `round(CARD_MIN_HEIGHT × φ)`（UC-003） |
| `CARD_MIN_HEIGHT` | 108 px | 10pt 3 行が収まる**下限**高さ（UC-003）。タイトル改行時はこれ以上に伸ばす |
| `CARD_LABEL_WRAP` | 155 px | タイトル・期限 `wraplength`（`CARD_MIN_WIDTH - 20`） |
| タイトルフォント pt | **10** bold | カードタイトル（medium 基準） |
| 期限ラベルフォント pt | **10** | カード期限表示 |
| 進捗ラベルフォント pt | **10** bold | 進捗バー中央 `%` |
| `PROGRESS_BAR_HEIGHT` | 16 px | 進捗バー |
| `CARD_FRAME_PAD` | 6 px | カード外枠内余白 |
| `CARD_TITLE_FRAME_PAD` | 5 × 3 px | タイトル枠内余白 |
| `CARD_DUE_PANEL_PAD` | 5 × 2 px | 期限パネル内余白 |
| `CARD_DUE_SECTION_GAP` | 3 px | タイトル行と期限行の間隔 |
| `CARD_PROGRESS_SECTION_GAP` | 4 px | 期限行と進捗バーの間隔 |
| `CARD_FRAME_BORDER` | 1 px | カード外枠線（**スケールしない**） |
| `CARD_TITLE_FRAME_BORDER` | 1 px | タイトル枠線 |
| `CARD_DUE_PANEL_BORDER` | 1 px | 期限パネル枠線 |
| `DUE_PICKER_PANEL_WIDTH` | 240 px | 期限編集パネル幅 |
| `MENU_CIRCLE_SIZE` | 36 px | メニューパネル円ボタン（UC-002） |
| メニュー円フォント pt | **14** bold | ＋ / ⚙ / × / `<` |
| 期限パネル月ラベル pt | **9** bold | `due_date_picker` |
| 期限パネル日ボタン pt | **8** | `due_date_picker` |

**スケール係数**

| ui_size | scale |
|---------|-------|
| `small` | 0.85 |
| `medium` | 1.0 |
| `large` | 1.15 |
| `xlarge` | 1.25 |

**配置への影響**
- UC-004 の新規カード配置幅はスケール後の `CARD_MIN_WIDTH + 2 * CARD_FRAME_BORDER` を用いる
- メニューパネルのヒット判定・展開幅はスケール後の `MENU_CIRCLE_SIZE` に追従する
- カードの保存座標（`x`, `y`）はスケール・フォント変更で **書き換えない**

---

## UC-010: UI フォント

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-027 |
| 関連 AC | AC-027-01, AC-027-02, AC-027-03 |
| 実装 | `src/petatto_kanban/display/ui_font.py`, `display/ui_font_labels.py`, `display/ui_metrics.py`, `app.py`, `card_renderer.py`, `display/ui_chrome.py`, `menu_panel.py`, `due_date_picker.py` |

`ui_font`（`settings.json`）に応じて、カード・メニュー・期限パネル等の **フォントファミリー** を切り替える。サイズ（pt）は UC-009 のスケールを用い、本 UC ではファミリー名のみを定義する。

| ui_font（JSON） | 設定 UI ラベル | tkinter 第 1 要素 |
|-----------------|----------------|-------------------|
| `segoe_ui` | Segoe UI | `Segoe UI` |
| `meiryo` | メイリオ | `Meiryo` |
| `yu_gothic_ui` | 游ゴシック | `Yu Gothic UI` |
| `ms_gothic` | MS ゴシック | `MS Gothic` |

**適用範囲**
- カード: タイトル、期限ラベル、進捗 `%`、インライン編集 `Entry`
- メニューパネル: 円ボタン内テキスト（＋ / ⚙ / × / `<`）
- 期限編集パネル: 月見出し・曜日行・日ボタン（`ttk.Button` のテーマ字体は対象外）

**フォールバック**
- 設定値が不正・欠損 → `segoe_ui`
- 指定ファミリーが OS に存在しない → 実行時に `Segoe UI` を使用（`font.actual()` 等で検証）

---

## UC-011: UI カラーテーマ

| 属性 | 値 |
|------|-----|
| 関連 FR | FR-028 |
| 関連 AC | AC-028-01, AC-028-02, AC-028-03 |
| 実装 | `src/petatto_kanban/display/ui_theme.py`, `display/ui_theme_labels.py`, `display/settings.py`, `display/settings_dialog_panels.py`, `display/settings_actions.py`, `display/ui_chrome.py`, `card_renderer.py`, `menu_panel.py`, `due_date_picker.py`, `app.py` |

`ui_theme`（`settings.json`）に応じて、UI 要素の **背景色・文字色** を切り替える。フォント（UC-010）・サイズ（UC-009）とは独立。

### 配色トークン

| トークン | 適用箇所 |
|----------|----------|
| `card_bg` / `card_fg` | カード枠背景、タイトル文字、インライン編集 `Entry` |
| `menu_fill` / `menu_fg` / `menu_outline` | メニューパネル円ボタンの塗り・文字・枠線 |
| `progress_track_bg` | 進捗バーの未達部分（トラック） |
| `due_future_bg` / `due_future_fg` | カード期限パネル（**未来**の期限） |
| `due_none_bg` / `due_none_fg` | カード期限パネル（**期限なし**） |
| `due_picker_bg` / `due_picker_fg` | 期限編集パネルの枠・見出し・通常日ボタン（非ハイライト） |

### テーマ非適用（固定色）

状態識別のため、以下は **全テーマ共通** で現行実装の色を維持する。

| 定数 / 関数 | 色の意味 | 参照 |
|-------------|----------|------|
| `DUE_PANEL_TODAY_BG` / `DUE_PANEL_TODAY_FG` | カード期限パネル **当日**（黄系） | `due_date.py` |
| `DUE_PANEL_OVERDUE_BG` / `DUE_PANEL_OVERDUE_FG` | カード期限パネル **超過**（赤系） | `due_date.py` |
| `progress_color(percent)` | 進捗バー **塗り**（赤→黄→緑） | `progress.py` |
| `CALENDAR_TODAY_BUTTON_BG` / `CALENDAR_TODAY_BUTTON_FG` | カレンダー **当日**ボタン（緑） | `due_date.py` |

**その他非適用**
- オーバーレイ透過色 `TRANSPARENT_COLOR`（`transparent.py`）
- OS 標準の `messagebox` / 確認ダイアログ

### 可読性

- 各テーマの `*_bg` と `*_fg` の組は、通常テキストで **コントラスト比 4.5:1 以上** を満たすこと（目視 + 実装時に WCAG 2.1 相当で確認）
- 進捗バー中央 `%` 文字色は、塗り幅に応じた既存のコントラスト判定（`progress >= 55` で白文字）を維持

### プリセット一覧（10 種）

| ui_theme | UI ラベル | 概要 |
|----------|-----------|------|
| `default` | Default | 現行既定（クリーム地・ダークグレー文字） |
| `dark` | ダーク | 黒に近い背景・白文字 |
| `sandy` | サンディ | 砂浜・ベージュ系の暖色 |
| `forest` | フォレスト | 深緑・アースグリーン系 |
| `fancy` | ファンシー | ラベンダー・パープル系 |
| `ocean` | オーシャン | 水色・ネイビー系 |
| `sunset` | サンセット | コーラル・夕焼け系 |
| `slate` | スレート | クールグレー・スレートブルー系 |
| `rose` | ローズ | ローズピンク系 |
| `midnight` | ミッドナイト | 深夜のネイビー・ダークブルー系 |

### パレット定義（`display/ui_theme.py` 予定）

色は `#RRGGBB` 形式。実装時は本表を `UiThemePalette` 等としてコード化する。

#### default（現行）

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#fffef8` / `#222222` |
| menu_fill / menu_fg / menu_outline | `#ffffff` / `#333333` / `#888888` |
| progress_track_bg | `#e8e8e8` |
| due_future_bg / due_future_fg | `#f5f5f0` / `#444444` |
| due_none_bg / due_none_fg | `#f5f5f0` / `#666666` |
| due_picker_bg / due_picker_fg | `#f5f5f0` / `#222222` |

#### dark

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#1a1a1a` / `#f2f2f2` |
| menu_fill / menu_fg / menu_outline | `#2b2b2b` / `#eeeeee` / `#555555` |
| progress_track_bg | `#333333` |
| due_future_bg / due_future_fg | `#242424` / `#cccccc` |
| due_none_bg / due_none_fg | `#242424` / `#aaaaaa` |
| due_picker_bg / due_picker_fg | `#222222` / `#e8e8e8` |

#### sandy

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#faf6ef` / `#3d3429` |
| menu_fill / menu_fg / menu_outline | `#fff8ee` / `#4a4035` / `#c4b8a8` |
| progress_track_bg | `#e8dfd0` |
| due_future_bg / due_future_fg | `#f0e8da` / `#5c5044` |
| due_none_bg / due_none_fg | `#f0e8da` / `#7a6f62` |
| due_picker_bg / due_picker_fg | `#f5ede3` / `#3d3429` |

#### forest

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#f4f9f4` / `#1b3d2a` |
| menu_fill / menu_fg / menu_outline | `#e8f5e9` / `#1b4332` / `#6b9080` |
| progress_track_bg | `#d4e8d4` |
| due_future_bg / due_future_fg | `#e0efe0` / `#2d5a3d` |
| due_none_bg / due_none_fg | `#e0efe0` / `#4a6b55` |
| due_picker_bg / due_picker_fg | `#edf5ed` / `#1b3d2a` |

#### fancy

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#faf5ff` / `#3d2a4a` |
| menu_fill / menu_fg / menu_outline | `#f3e8ff` / `#5b3a6e` / `#b794c9` |
| progress_track_bg | `#eadcf5` |
| due_future_bg / due_future_fg | `#efe4f8` / `#4a3560` |
| due_none_bg / due_none_fg | `#efe4f8` / `#6b5580` |
| due_picker_bg / due_picker_fg | `#f5effa` / `#3d2a4a` |

#### ocean

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#f0f8ff` / `#0d3b5c` |
| menu_fill / menu_fg / menu_outline | `#e3f2fd` / `#1565c0` / `#64b5f6` |
| progress_track_bg | `#cce4f5` |
| due_future_bg / due_future_fg | `#ddeef8` / `#1a5276` |
| due_none_bg / due_none_fg | `#ddeef8` / `#4a7a9a` |
| due_picker_bg / due_picker_fg | `#e8f4fc` / `#0d3b5c` |

#### sunset

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#fff8f3` / `#4a2c2a` |
| menu_fill / menu_fg / menu_outline | `#ffe8e0` / `#8b4513` / `#e8a598` |
| progress_track_bg | `#f5ddd4` |
| due_future_bg / due_future_fg | `#fceee8` / `#6b3a35` |
| due_none_bg / due_none_fg | `#fceee8` / `#8a5a55` |
| due_picker_bg / due_picker_fg | `#fff0ea` / `#4a2c2a` |

#### slate

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#f5f7fa` / `#1e293b` |
| menu_fill / menu_fg / menu_outline | `#eef2f7` / `#334155` / `#94a3b8` |
| progress_track_bg | `#dde3ea` |
| due_future_bg / due_future_fg | `#e8edf2` / `#334155` |
| due_none_bg / due_none_fg | `#e8edf2` / `#64748b` |
| due_picker_bg / due_picker_fg | `#edf1f5` / `#1e293b` |

#### rose

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#fff5f7` / `#4a1942` |
| menu_fill / menu_fg / menu_outline | `#fce4ec` / `#880e4f` / `#f48fb1` |
| progress_track_bg | `#f8d7e0` |
| due_future_bg / due_future_fg | `#fdeef2` / `#6b2149` |
| due_none_bg / due_none_fg | `#fdeef2` / `#8a4560` |
| due_picker_bg / due_picker_fg | `#fef0f3` / `#4a1942` |

#### midnight

| トークン | 値 |
|----------|-----|
| card_bg / card_fg | `#1e2433` / `#e8eaf0` |
| menu_fill / menu_fg / menu_outline | `#2a3142` / `#d0d4de` / `#5c6a82` |
| progress_track_bg | `#323848` |
| due_future_bg / due_future_fg | `#252b3a` / `#c0c8d4` |
| due_none_bg / due_none_fg | `#252b3a` / `#9098a8` |
| due_picker_bg / due_picker_fg | `#222838` / `#e0e4ec` |

**フォールバック**
- 設定値が不正・欠損 → `default`
- 実装時、パレット取得 API は `palette_for_theme(UiTheme)` を公開し、描画モジュールは定数直参照をやめてパレット経由にリファクタする

---

## UC-007: 列レイアウト（M2）

M1 では 3 列カンバン UI は提供しない。M2 で FR-012 導入時に本 UC を復活する。

---

## 改訂履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2026-08-12 | 3 列カンバン + ヘッダー UI |
| 1.1.0 | 2026-08-12 | オーバーレイ + 自由配置カード + ツールバー UI |
| 1.2.0 | 2026-08-12 | ディスプレイ選択を設定へ移動。右クリック離しで削除 |
| 1.3.0 | 2026-08-12 | 編集ボタン削除。タイトルダブルクリックでインライン編集 |
| 1.4.0 | 2026-08-12 | カード最小サイズ追加。タイトルもドラッグ移動・右クリック削除可能 |
| 1.5.0 | 2026-08-12 | カード追加を即時作成（初期タイトル `新しいタスク`）。入力ダイアログ廃止 |
| 1.6.0 | 2026-08-12 | タイトル表示を枠線付き内側フレームで囲む |
| 1.7.0 | 2026-08-12 | カード追加位置をツールバー付近に変更。追加直後インライン編集を自動開始 |
| 1.8.0 | 2026-08-12 | カード進捗率バー（0〜100%・色グラデーション・ホイール操作） |
| 1.9.0 | 2026-08-12 | カード期限パネル・フロートカレンダー編集（FR-014） |
| 1.9.1 | 2026-08-12 | 期限編集 UI をカード外フロートパネルへ変更 |
| 1.9.2 | 2026-08-12 | 進捗バーでもドラッグ・右クリック削除。カレンダー当日ボタンを緑色に |
| 1.9.3 | 2026-08-12 | タイトル編集中にタイトル以外をクリックで編集確定 |
| 1.9.4 | 2026-08-12 | 期限編集中にパネル外クリックでキャンセル（閉じると同様） |
| 1.9.5 | 2026-08-12 | 期限編集の開始を2回目の離しで反応（遅延なし） |
| 1.9.6 | 2026-08-12 | 期限編集の単回離しキャンセル、インライン編集確定タイミングを明記 |
| 1.9.7 | 2026-08-12 | タイトル編集の開始を2回目の離しで反応（`<Double-Button-1>` 廃止） |
| 2.0.0 | 2026-08-12 | ツールバーをメニューパネル（円形＜・ホバー展開・ドラッグ移動）に置換 |
| 2.0.1 | 2026-08-12 | ホバー展開に **＋**（カード追加）ボタンを追加 |
| 2.0.2 | 2026-08-12 | ホバー展開を左方向に固定。メニューフレーム背景を透過 |
| 2.0.3 | 2026-08-12 | ＋・⚙・× ボタンを `<` パネル同型の円形 UI に統一 |
| 2.0.4 | 2026-08-12 | メニューボタン（＋・⚙・×）を `<ButtonRelease-1>` で反応するよう明記・実装 |
| 2.0.5 | 2026-08-12 | 展開フラッシュ修正（先に位置補正）。ボタン間の白矩形を廃止 |
| 2.0.6 | 2026-08-12 | 展開・収納時は `anchor=NE` で `<` 右端固定（ホバー解除フラッシュ解消） |
| 2.0.7 | 2026-08-12 | 展開パネルと `×` / `<` 円の間隔をゼロに |
| 2.1.0 | 2026-08-13 | UC-002 を現行実装に同期。`menu_panel.py` リファクタ・テスト追加 |
| 2.1.1 | 2026-08-13 | UC-004 新規カード配置をメニューパネル直下・右端揃えに変更 |
| 2.1.2 | 2026-08-13 | UC-004 配置契約を詳細化。`MenuPanelRect` / `new_card_placement` へリファクタ |
| 2.1.3 | 2026-08-13 | UC-004 右端揃えを NE アンカー基準に修正。連続追加は左下 12px ずつ |
| 2.1.4 | 2026-08-13 | UC-004 縦余白 2px・右端から 28px 左インデントに調整 |
| 2.1.5 | 2026-08-13 | UC-004 左インデント 128px・モニター内クランプ追加 |
| 2.2.0 | 2026-08-13 | UC-001/UC-006: デスクトップモード追加。設定でオーバーレイと切替 |
| 2.2.1 | 2026-08-13 | UC-006 実装を `settings_dialog.py` / `mode_labels.py` に分離 |
| 2.2.2 | 2026-08-13 | UC-002: デスクトップモードでメニューパネルのみ常時最前面（`menu_panel_host`） |
| 2.2.3 | 2026-08-13 | UC-002: メニューアクティブ時にカード等を一時最前面（DM-DESKTOP-02） |
| 2.2.4 | 2026-08-13 | UC-002: 他アプリアクティブ時の即時背面復帰（DM-DESKTOP-03） |
| 2.2.5 | 2026-08-13 | Z オーダー制御を `desktop_board_controller.py` に集約 |
| 2.3.0 | 2026-08-13 | UC-006: 設定ダイアログを「表示」「システム」タブに分割 |
| 2.3.1 | 2026-08-13 | UC-006 システムタブ: アプリ終了時の確認オプション（`confirm_exit`） |
| 2.3.2 | 2026-08-13 | UC-006 システムタブ: 「全てのカードを削除」ボタン（FR-005） |
| 2.3.3 | 2026-08-13 | UC-006 実装リファクタ（`settings_dialog_labels` / `settings_dialog_panels` / `settings_actions`） |
| 2.4.0 | 2026-08-13 | UC-006 表示タブ: UI サイズ設定（FR-026）。UC-009 UI スケール契約を追加 |
| 2.5.0 | 2026-08-13 | UC-006 表示タブ: フォント設定（FR-027）。UC-010 UI フォント契約を追加 |
| 2.6.0 | 2026-08-13 | FR-027 実装。UC-009/UC-010 を `ui_metrics.py` で合成 |
| 2.7.0 | 2026-08-13 | UC-006 テーマタブ・UC-011 UI カラーテーマ契約（FR-028） |
| 2.8.0 | 2026-08-13 | FR-028 実装（10 種カラーテーマ・期限/進捗の意味色は固定） |
| 2.9.0 | 2026-08-14 | UC-006 システムタブ: Windows ログオン時自動起動（FR-029） |
| 2.9.1 | 2026-08-14 | UC-006: 自動起動失敗時は全項目ロールバック。起動コマンド解決を分離 |
| 2.9.2 | 2026-08-14 | UC-006: 自動起動は Windows 11 以降のみ。非 Windows 無効化の記述を削除 |
| 2.10.0 | 2026-08-14 | UC-006 操作タブ・UC-012 キーボードショートカット（FR-030、既定 Ctrl+Shift+N） |
| 2.10.1 | 2026-08-14 | UC-006 操作タブ・UC-012 を実装（`system/hotkey.py` / RegisterHotKey） |
| 2.10.2 | 2026-08-14 | UC-012: コード正規化を `shortcut.py` に分離。失敗時は全項目ロールバック |
| 2.10.3 | 2026-08-14 | UC-012: WM_HOTKEY はメッセージ専用ウィンドウで受信（Tk WndProc 差し替えを廃止） |
| 2.10.4 | 2026-08-14 | UC-012: Python WndProc を廃止。専用スレッド + `GetMessage` + Tk `poll()` |
| 2.10.5 | 2026-08-14 | UC-012: Win32 ポンプを `hotkey_pump.py` に分離。セッションは `hotkey.py` |
| 2.11.0 | 2026-08-14 | UC-003: タイトル改行時はカード高さを下限以上に伸ばし、幅は固定 |
| 2.11.1 | 2026-08-14 | UC-003: 枠サイズ決定を `card_frame.py` に分離。基準寸法は `card_layout.py` |
| 2.12.0 | 2026-08-14 | UC-006 システムタブ: GitHub Issue 任意起票（FR-032）。エラーログは FR-031 |
| 2.12.1 | 2026-08-14 | UC-006 システムタブ: 起票可否の ON/OFF・即時適用・永続化を明記（FR-032） |
