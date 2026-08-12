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
