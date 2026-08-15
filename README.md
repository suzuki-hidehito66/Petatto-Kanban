# Petatto-Kanban

**ペタッとカンバン** — 付箋のようにタスクを貼れる、単一ユーザー向け Windows デスクトップカンバンアプリ

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Windows 11+](https://img.shields.io/badge/platform-Windows%2011%2B-lightgrey)](https://www.microsoft.com/windows)

---

## このアプリについて

Petatto-Kanban は **1 人の PC 上で完結** するタスク管理アプリです。ログイン不要・クラウド不要で、カードを画面上に自由に配置して進められます。

- **オーバーレイモード** — 指定ディスプレイ全画面・透過・最前面（既定）
- **デスクトップモード** — 通常ウィンドウより背面に表示
- **カード** — タイトル編集、期限（当日黄 / 超過赤）、進捗バー（0〜100%）
- **見た目** — UI サイズ（小 / 標準 / 大 / 極大）、フォント、10 種カラーテーマ

配布形式は PyInstaller による単一 `.exe` です。

---

## ダウンロード（一般ユーザー向け）

最新版は GitHub Releases から入手できます。

**[Releases ページ](https://github.com/suzuki-hidehito66/Petatto-Kanban/releases)** → `Petatto-Kanban.exe` をダウンロード → ダブルクリックで起動

| 項目 | 要件 |
|------|------|
| OS | **Windows 11 以降** |
| ネットワーク | 不要（オフライン動作） |
| インストール | 不要（ポータブル exe） |

---

## 主な機能

| カテゴリ | 内容 |
|----------|------|
| カード操作 | 追加（＋ボタン）、ドラッグ移動、右クリック離しで削除 |
| タイトル | ダブルクリック相当の操作でインライン編集 |
| 期限 | カレンダーで設定。「期限なし」も可 |
| 進捗 | ホバー中にマウスホイールで ±10% |
| 設定 | 表示モード、ディスプレイ、UI サイズ、フォント、テーマ、削除確認 |
| データ | すべてローカル JSON に自動保存 |

---

## データの保存場所

ユーザーデータはリポジトリ外のホームディレクトリに保存されます（**公開リポジトリに含まれません**）。

```
%USERPROFILE%\.petatto-kanban\
├── board.json      # カード・座標・進捗・期限
└── settings.json   # 表示モード・UI サイズ・フォント・テーマ等
```

バックアップする場合は上記フォルダをコピーしてください。

---

## 開発者向け

### 必要条件

- Python **3.11 以上**
- **Windows 11 以降**（exe ビルド・実行時）

### セットアップ

```bash
git clone https://github.com/suzuki-hidehito66/Petatto-Kanban.git
cd Petatto-Kanban
python -m pip install -e ".[dev]"
```

### 開発モードで起動

```bash
python -m petatto_kanban
```

### テスト・Lint

```bash
python -m pytest
python -m ruff check src tests
```

### Windows `.exe` のローカルビルド

`build_exe.bat` / `build_exe.ps1` のコンソール出力は **ASCII（英語）** です（cmd / PowerShell 5.x の文字化け回避）。

**ビルド前:** 実行中の `Petatto-Kanban.exe` を終了してください。起動中だと `dist\Petatto-Kanban.exe` がロックされ PyInstaller が失敗します。

```cmd
scripts\build_exe.bat
```

または:

```powershell
.\scripts\build_exe.ps1
```

成果物: `dist\Petatto-Kanban.exe`

---

## ブランチ運用（コントリビュータ向け）

| ブランチ | 用途 |
|----------|------|
| `main` | 本番。squash マージ 1 回 = リリース 1 件。CI が exe ビルド + GitHub Release |
| `test` | 動作確認用。`dev_*` の squash を載せる。リリース後は `main` に一致させる |
| `dev_*` | 機能開発。**`main` から作成**し、PR は **`test` 向け**（squash） |

**流れ**

1. `dev_<name>` を `main` から切る（未リリースの `test` 上の変更に依存するときだけ `test` から）
2. `dev_*` → `test` を **squash マージ**して動作確認する
3. 確認できたら `test` → `main` の PR を **squash マージ**する（`dev_*` から `main` へは出さない）
4. **`main` マージ直後**に `test` を `main` へ合わせる。CI（`sync-test-to-main.yml`）が自動で行う。失敗時だけ手動で `reset --hard origin/main` と `--force-with-lease` push

`test` の force-push はリリース後の同期だけ。開発中は squash PR のみ（merge commit なし）。`test` を保護する場合は GitHub Actions の force-push を許可してください。

リリース前は `pyproject.toml` / `__init__.py` / `docs/spec/11-release-plan.md` の **3 箇所でバージョンを同期** してください（`tests/test_release_version.py` で検証）。

---

## CI / リリース

| イベント | 動作 |
|----------|------|
| `main` 向け PR | Windows でテスト・Lint・exe ビルド |
| `main` 向け PR（元ブランチ） | **`test` のみ**（`enforce-test-to-main.yml`） |
| `main` へマージ | GitHub Release 作成（`v{バージョン}` タグ、`Petatto-Kanban.exe` 添付）。続けて `sync-test-to-main.yml` が `test` を `main` に揃える |

### GitHub Actions 権限（メンテナ向け）

Release 作成にはリポジトリ Settings → Actions → **Read and write permissions** が必要です。403 になる場合は [Issue](https://github.com/suzuki-hidehito66/Petatto-Kanban/issues) で確認してください。

**`main` ブランチ保護（推奨）:** Branch protection で PR 必須に加え、必須ステータスチェックに `check-source-branch`（`Enforce test to main`）と `build`（`Build Windows EXE`）を登録してください。

**`test` ブランチ保護:** force-push を禁止する場合は、`sync-test-to-main.yml` が失敗します。Actions（`github-actions[bot]`）の force-push を許可するか、保護を付けないでください。

---

## ドキュメント

| ファイル | 内容 |
|----------|------|
| [docs/SPECIFICATION.md](docs/SPECIFICATION.md) | SDD 仕様書索引 |
| [docs/spec/](docs/spec/) | 要件・受け入れ基準・UI 契約 |
| [docs/PYTHON_CODING_RULES.md](docs/PYTHON_CODING_RULES.md) | Python コーディングルール |
| [docs/spec/11-release-plan.md](docs/spec/11-release-plan.md) | リリース計画・バージョン管理 |

---

## 公開・セキュリティに関する注意

- 本リポジトリには **API キーやパスワードを含めない** でください
- ユーザーの `board.json` / `settings.json` をコミットしないでください
- 脆弱性報告は GitHub Security Advisories または Issue をご利用ください

---

## ライセンス

[MIT License](LICENSE) — Copyright (c) suzuki-hidehito66

---

## ステータス

M1 MVP 開発中（Alpha）。機能追加・仕様変更が続く可能性があります。本番利用は自己責任でお願いします。
