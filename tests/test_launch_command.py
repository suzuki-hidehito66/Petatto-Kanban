"""launch_command のテスト."""

from __future__ import annotations

from pathlib import Path

from petatto_kanban.system.launch_command import resolve_launch_command


def test_resolve_launch_command_frozen() -> None:
    command = resolve_launch_command(
        frozen=True,
        executable=r"C:\Apps\Petatto-Kanban.exe",
    )
    assert command.endswith('Petatto-Kanban.exe"')
    assert command.startswith('"')
    assert " -m " not in command


def test_resolve_launch_command_dev_uses_module() -> None:
    command = resolve_launch_command(frozen=False)
    assert command.endswith(" -m petatto_kanban")
    assert command.startswith('"')


def test_resolve_launch_command_prefers_pythonw(tmp_path: Path) -> None:
    python_exe = tmp_path / "python.exe"
    pythonw_exe = tmp_path / "pythonw.exe"
    python_exe.write_text("", encoding="utf-8")
    pythonw_exe.write_text("", encoding="utf-8")

    command = resolve_launch_command(frozen=False, executable=python_exe)
    assert str(pythonw_exe.resolve()) in command
    assert command.endswith(" -m petatto_kanban")


def test_resolve_launch_command_keeps_python_when_pythonw_missing(tmp_path: Path) -> None:
    python_exe = tmp_path / "python.exe"
    python_exe.write_text("", encoding="utf-8")

    command = resolve_launch_command(frozen=False, executable=python_exe)
    assert str(python_exe.resolve()) in command
    assert "pythonw.exe" not in command
