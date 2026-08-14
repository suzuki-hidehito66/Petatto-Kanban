"""ログオン時に実行するコマンド行の解決（tkinter / winreg 非依存）."""

from __future__ import annotations

import sys
from pathlib import Path

MODULE_LAUNCH = "-m petatto_kanban"


def resolve_launch_command(
    *,
    frozen: bool | None = None,
    executable: str | Path | None = None,
) -> str:
    """ログオン時に実行するコマンド行を返す.

    Args:
        frozen: PyInstaller 実行なら True。省略時は ``sys.frozen``。
        executable: 実行ファイルパス。省略時は ``sys.executable``。
    """
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    exe_path = Path(sys.executable if executable is None else executable).resolve()
    if is_frozen:
        return f'"{exe_path}"'

    launch_exe = _prefer_pythonw(exe_path)
    return f'"{launch_exe}" {MODULE_LAUNCH}'


def _prefer_pythonw(executable: Path) -> Path:
    """python.exe ならコンソールなしの pythonw.exe を優先する."""
    if executable.name.lower() != "python.exe":
        return executable
    pythonw = executable.with_name("pythonw.exe")
    if pythonw.is_file():
        return pythonw
    return executable
