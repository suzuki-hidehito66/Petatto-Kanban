# 04 — 非機能要件

| 項目 | 内容 |
|------|------|
| ステータス | Active |

---

## 要件一覧

| ID | カテゴリ | 要件 | 優先度 | ステータス | マイルストーン |
|----|----------|------|--------|------------|----------------|
| [NFR-001](#nfr-001-パフォーマンス) | パフォーマンス | カード 100 件で UI 操作が実用的 | Must | specified | M1 |
| [NFR-002](#nfr-002-ウィンドウサイズ) | 可用性 | 最小 960×540 で全列が表示可能 | Must | implemented | M1 |
| [NFR-003](#nfr-003-データ整合性) | 信頼性 | 保存・読込でデータ欠損がない | Must | verified | M1 |
| [NFR-004](#nfr-004-配布形式) | 配布 | Windows `.exe` 単一ファイルで配布 | Must | implemented | M1 |
| [NFR-005](#nfr-005-依存関係) | 保守性 | MVP ランタイム依存は標準ライブラリのみ | Must | verified | M1 |
| [NFR-006](#nfr-006-コード品質) | 保守性 | Ruff Lint エラー 0 | Must | verified | M1 |
| [NFR-007](#nfr-007-テスト) | 品質 | モデル・永続化に pytest カバー | Must | verified | M1 |
| [NFR-008](#nfr-008-単一ユーザー独立動作) | アーキテクチャ | 単一ユーザー・オフライン・独立 .exe 動作 | Must | verified | M1 |
| [NFR-011](#nfr-011-プラットフォーム) | 互換性 | Windows 11 以降をサポート | Must | specified | M1 |
| NFR-009 | アクセシビリティ | キーボードによるカード移動 | Could | deferred | M2 |
| NFR-010 | 国際化 | UI 文言の i18n 対応 | Won't (M2) | deferred | M3 |

---

## 詳細

### NFR-001: パフォーマンス

| 属性 | 値 |
|------|-----|
| ステータス | specified |
| 関連 AC | AC-NFR-001-01 |
| 検証方法 | 手動（M1）、自動ベンチマーク（M2 検討） |

**要件**  
1 ボード・100 カード程度で、カード追加・移動・保存が 1 秒以内に完了すること。

**測定条件**
- **Windows 11 以降**、一般的なデスクトップ PC
- カードは 3 列に均等分散

---

### NFR-002: ウィンドウサイズ

| 属性 | 値 |
|------|-----|
| ステータス | implemented |
| 実装 | `src/petatto_kanban/app.py` (`WINDOW_MIN_WIDTH`, `WINDOW_MIN_HEIGHT`) |

**要件**  
ウィンドウ最小サイズ 960 × 540 px で 3 列が横並び表示されること。

---

### NFR-003: データ整合性

| 属性 | 値 |
|------|-----|
| ステータス | verified |
| 関連 AC | AC-007-01, AC-007-02 |
| テスト | `tests/test_models_and_storage.py` |

**要件**  
save → load のラウンドトリップで Board / Column / Card の全属性が一致すること。

---

### NFR-004: 配布形式

| 属性 | 値 |
|------|-----|
| ステータス | implemented |
| 実装 | `petatto-kanban.spec`, `scripts/build_exe.bat` |
| CI | `.github/workflows/build-windows.yml` |

**要件**  
PyInstaller により `dist/Petatto-Kanban.exe` を生成できること。  
コンソールウィンドウは表示しない（`console=False`）。

---

### NFR-005: 依存関係

| 属性 | 値 |
|------|-----|
| ステータス | verified |
| 実装 | `pyproject.toml` `[project] dependencies = []` |

**要件**  
MVP の実行時依存は Python 標準ライブラリ（tkinter 含む）のみ。

---

### NFR-006: コード品質

| 属性 | 値 |
|------|-----|
| ステータス | verified |
| 検証 | `python -m ruff check src tests` |

**要件**  
Ruff 設定（`pyproject.toml`）に従い、Lint エラー 0 であること。

---

### NFR-007: テスト

| 属性 | 値 |
|------|-----|
| ステータス | verified |
| 検証 | `python -m pytest` |

**要件**  
ドメインモデル（`models.py`）と永続化（`storage.py`）に対する自動テストが存在し、CI で実行されること。

**注記**  
GUI（`app.py`）の自動テストは M2 で検討（FR 実装後に AC 追加）。

---

### NFR-008: 単一ユーザー独立動作

| 属性 | 値 |
|------|-----|
| ステータス | verified |
| 関連 AC | AC-NFR-008-01, AC-NFR-008-02 |
| 実装 | アーキテクチャ全体（ネットワークコードなし） |

**要件**  
M1 MVP は **単一ユーザーの独立したデスクトップアプリケーション** として動作すること。

| # | 条件 |
|---|------|
| 1 | ユーザー認証・ログイン機能を持たない |
| 2 | ネットワーク通信（HTTP/WebSocket 等）を行わない |
| 3 | データはローカル JSON ファイルのみに保存する。エラーログは [FR-031](./03-functional-requirements.md#fr-031-ローカルエラーログ) のローカルファイル |
| 4 | `.exe` 単体の起動で全 M1 機能が利用できる |
| 5 | マルチユーザー・共同編集機能を持たない |

**検証**
- コードベースに `requests` / `urllib` 等のネットワーク呼び出しがないこと
- `pyproject.toml` の runtime 依存が空であること
- 手動: ネットワーク切断状態で `.exe` が動作すること（AC-NFR-008-02）

---

### NFR-011: プラットフォーム

| 属性 | 値 |
|------|-----|
| ステータス | specified |
| 関連 AC | AC-NFR-011-01 |
| 実装 | ドキュメント・CI（`windows-latest` = Windows Server 2022 / Win11 相当） |

**要件**  
本アプリの **サポート対象 OS は Windows 11 以降** とする。

| # | 条件 |
|---|------|
| 1 | Windows 11 およびそれ以降のメジャーバージョンで動作すること |
| 2 | Windows 10 以下・macOS・Linux は **非サポート**（劣化動作や受け入れ基準は定義しない） |
| 3 | 開発・CI・exe ビルドは Windows 11 相当環境を基準とする |

**根拠**  
表示モード（透過・Z オーダー・マルチディスプレイ）で Windows 11 の DWM / Win32 API を前提とする。
