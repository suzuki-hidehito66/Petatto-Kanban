# Petatto-Kanban

ペタッとカンバン — **単一ユーザー向けの独立した Windows デスクトップ**カンバンタスク管理アプリ（`.exe`）

## 概要

1 人のユーザーが自分の PC 上で完結して使えるカンバンアプリです。  
**M1 ではオーバーレイモード**（指定ディスプレイ全画面・透過・最前面表示）を既定 UI とし、カードはドラッグで自由配置できます。PyInstaller により `.exe` として配布します。

## 必要条件

- Python 3.11 以上（開発時）
- **Windows 11 以降**（`.exe` ビルド・実行時）

## セットアップ

```bash
git clone https://github.com/suzuki-hidehito66/Petatto-Kanban.git
cd Petatto-Kanban
python -m pip install -e ".[dev]"
```

## 開発モードで起動

```bash
python -m petatto_kanban
```

または:

```bash
petatto-kanban
```

## テスト・Lint

```bash
python -m pytest
python -m ruff check src tests
```

## Windows 実行ファイル（.exe）のビルド

`build_exe.bat` / `build_exe.ps1` のコンソール出力は **ASCII（英語）** です。UTF-8 無 BOM の日本語は cmd / PowerShell 5.x で文字化けするため。

**ビルド前:** 実行中の `Petatto-Kanban.exe` を終了してください。起動中だと `dist\Petatto-Kanban.exe` がロックされ PyInstaller が失敗します（`WinError 5`）。スクリプトは起動検知と旧 exe の退避を試みます。

### 方法 1: バッチファイル

```cmd
scripts\build_exe.bat
```

### 方法 2: PowerShell

```powershell
.\scripts\build_exe.ps1
```

PowerShell 5.x では `"[INFO]"` のような角括弧付き二重引用符文字列が構文エラーになるため、ログは単一引用符・英語表記にしています。

### 方法 3: 手動

```cmd
python -m pip install -e ".[dev]"
python -m PyInstaller petatto-kanban.spec --noconfirm
```

ビルド成果物: `dist\Petatto-Kanban.exe`

## CI / リリース

| イベント | 動作 |
|----------|------|
| `main` 向け PR | Windows でテスト・Lint・exe ビルド、Artifact アップロード |
| PR を `main` にマージ | 上記に加え **GitHub Release** 作成（`v{バージョン}` タグ、`Petatto-Kanban.exe` 添付） |

ダウンロード: [Releases](https://github.com/suzuki-hidehito66/Petatto-Kanban/releases)

**バージョン更新**（リリース PR マージ前）: 次の 3 箇所を同じ SemVer に揃える。

1. `pyproject.toml` → `[project].version`
2. `src/petatto_kanban/__init__.py` → `__version__`
3. `docs/spec/11-release-plan.md` → アプリリリースバージョン表

同じバージョンで main に再マージするとタグが重複し Release ジョブが失敗します（意図的なガード）。

### GitHub Actions 権限（Release 作成に必要）

ワークフロー側: `release` ジョブに `permissions: contents: write` を設定済み。

リポジトリ側（初回または Release が 403 になる場合）:

1. GitHub リポジトリ → **Settings** → **Actions** → **General**
2. **Workflow permissions** で **Read and write permissions** を選択
3. **Save**

`GITHUB_TOKEN` に Release 作成・タグ push 権限が付与されます。

## データ保存場所

ボードデータは次の JSON ファイルに保存されます。

```
%USERPROFILE%\.petatto-kanban\board.json
```

## ドキュメント

| ファイル | 内容 |
|----------|------|
| [docs/SPECIFICATION.md](docs/SPECIFICATION.md) | **SDD 仕様書索引**（仕様駆動開発のエントリポイント） |
| [docs/spec/](docs/spec/) | 要件・受け入れ基準・トレーサビリティ等の詳細仕様 |
| [docs/PYTHON_CODING_RULES.md](docs/PYTHON_CODING_RULES.md) | Python コーディングルール |

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) を参照してください。
