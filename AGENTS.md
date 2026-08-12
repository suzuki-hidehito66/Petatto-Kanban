# AGENTS.md

## Cursor Cloud specific instructions

Petatto-Kanban is a Python 3.11+ tkinter desktop app. Linux dev VMs can run unit tests but **cannot fully verify overlay mode** (Win32 topmost, transparency, click-through) — that requires Windows 11+ manual testing.

### Standard commands

| Task | Command |
|------|---------|
| Install deps | `python3 -m pip install -e ".[dev]"` |
| Run app (needs display) | `python3 -m petatto_kanban` |
| Tests | `python3 -m pytest` |
| Lint | `python3 -m ruff check src tests` |
| Build `.exe` | Windows only: `scripts/build_exe.bat` — close running `Petatto-Kanban.exe` first |

### Services

No background server. The app is a single-process tkinter GUI. Start with `python3 -m petatto_kanban` in a tmux session when a display is available.

### Gotchas

- Use `python3`, not `python` (not on PATH in this environment).
- M1 default UI is **overlay mode** (`display/overlay.py`): fullscreen, topmost, transparent background; cards use `place(x, y)` with drag-to-move.
- Data paths: `%USERPROFILE%\.petatto-kanban\board.json` (schema v2, flat `cards` with `x`/`y`) and `settings.json` (`mode`, `monitor_index`, `confirm_delete`).
- Legacy `board.json` with `columns` is migrated on load.

See [README.md](README.md) and [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for full SDD docs.
