"""Prepare dist/ before PyInstaller overwrites Petatto-Kanban.exe."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXE_NAME = "Petatto-Kanban.exe"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def is_process_running(image_name: str) -> bool:
    """Return True if a Windows process with the given image name is running."""
    if sys.platform != "win32":
        return False

    result = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    return image_name.lower() in result.stdout.lower()


def _remove_or_rename(path: Path) -> bool:
    try:
        path.unlink()
        return True
    except OSError:
        pass

    backup = path.with_name(f"{path.name}.bak")
    try:
        if backup.exists():
            backup.unlink()
        path.rename(backup)
        return True
    except OSError:
        return False


def prepare() -> int:
    """Exit 0 when dist is ready for PyInstaller; 1 on failure."""
    dist_exe = _repo_root() / "dist" / EXE_NAME

    if is_process_running(EXE_NAME):
        print(f"ERROR: {EXE_NAME} is running. Close the app and run build again.")
        return 1

    if not dist_exe.exists():
        return 0

    if _remove_or_rename(dist_exe):
        if dist_exe.with_name(f"{EXE_NAME}.bak").exists():
            print(f"INFO: Renamed existing exe to {EXE_NAME}.bak")
        return 0

    print(f"ERROR: Cannot replace {dist_exe}.")
    print(f"ERROR: Close {EXE_NAME} (and antivirus scan if needed), then retry.")
    return 1


def main() -> None:
    raise SystemExit(prepare())


if __name__ == "__main__":
    main()
