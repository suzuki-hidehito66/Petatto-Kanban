@echo off
setlocal enabledelayedexpansion

REM Petatto-Kanban Windows executable (.exe) build script
REM Usage: scripts\build_exe.bat
REM Output: dist\Petatto-Kanban.exe
REM
REM Log messages are ASCII-only to avoid mojibake on Japanese Windows cmd.exe
REM when this file is saved as UTF-8 without BOM.

cd /d "%~dp0\.."

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11 or later.
    exit /b 1
)

echo INFO: Installing dependencies...
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -e ".[dev]"
if errorlevel 1 exit /b 1

echo INFO: Building .exe with PyInstaller...
python -m PyInstaller petatto-kanban.spec --noconfirm
if errorlevel 1 exit /b 1

echo SUCCESS: Build finished: dist\Petatto-Kanban.exe
endlocal
