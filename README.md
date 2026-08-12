# Petatto-Kanban

ペタッとカンバン — Python で動作する Windows デスクトップ向けカンバンタスク管理アプリ

## 概要

直感的な操作でタスクを管理できるカンバン方式のアプリケーションです。  
Python + tkinter で実装し、PyInstaller により Windows 実行ファイル（`.exe`）として配布できます。

## 必要条件

- Python 3.11 以上
- Windows（.exe ビルド・実行時）

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

### 方法 1: バッチファイル

```cmd
scripts\build_exe.bat
```

### 方法 2: PowerShell

```powershell
.\scripts\build_exe.ps1
```

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
| [docs/SPECIFICATION.md](docs/SPECIFICATION.md) | プロジェクト仕様書 |
| [docs/PYTHON_CODING_RULES.md](docs/PYTHON_CODING_RULES.md) | Python コーディングルール |

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) を参照してください。
