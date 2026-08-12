@echo off
setlocal enabledelayedexpansion

REM Petatto-Kanban Windows 実行ファイル (.exe) ビルドスクリプト
REM 使用方法: scripts\build_exe.bat

cd /d "%~dp0\.."

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python が見つかりません。Python 3.11 以上をインストールしてください。
    exit /b 1
)

echo [INFO] 依存関係をインストールしています...
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
if errorlevel 1 exit /b 1

echo [INFO] PyInstaller で .exe をビルドしています...
python -m PyInstaller petatto-kanban.spec --noconfirm
if errorlevel 1 exit /b 1

echo [SUCCESS] ビルド完了: dist\Petatto-Kanban.exe
endlocal
