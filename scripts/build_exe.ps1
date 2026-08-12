# Petatto-Kanban Windows 実行ファイル (.exe) ビルドスクリプト
# 使用方法: .\scripts\build_exe.ps1

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python が見つかりません。Python 3.11 以上をインストールしてください。"
}

Write-Host "[INFO] 依存関係をインストールしています..."
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

Write-Host "[INFO] PyInstaller で .exe をビルドしています..."
python -m PyInstaller petatto-kanban.spec --noconfirm

Write-Host "[SUCCESS] ビルド完了: dist\Petatto-Kanban.exe"
