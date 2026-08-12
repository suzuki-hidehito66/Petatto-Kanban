# Petatto-Kanban Windows executable (.exe) build script
# Usage: .\scripts\build_exe.ps1
# Output: dist\Petatto-Kanban.exe
#
# Note: Use single-quoted strings for log lines. Double quotes break on [INFO]/[ERROR]
# because PowerShell treats [name] as a type or array expression.

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error 'Python not found. Install Python 3.11 or later.'
}

Write-Host 'INFO: Installing dependencies...'
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'INFO: Building .exe with PyInstaller...'
python -m PyInstaller petatto-kanban.spec --noconfirm
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'SUCCESS: Build finished: dist\Petatto-Kanban.exe'
