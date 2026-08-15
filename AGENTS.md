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
- **GitHub Release**: main マージ時に `v{pyproject version}` で Release 作成。バージョンは `pyproject.toml` / `__init__.py` / `docs/spec/11-release-plan.md` を同期（`tests/test_release_version.py`）。
- Legacy `board.json` with `columns` is migrated on load.

See [README.md](README.md) and [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for full SDD docs.

### Git ブランチ運用

| ブランチ | 用途 | 履歴 |
|----------|------|------|
| `main` | 本番。マージ時に GitHub Release | リリース 1 件 = squash 1 コミット |
| `test` | 動作確認用の統合 | 機能 1 件 = squash 1 コミット。リリース後は `main` に一致させる |
| `dev_*` | テーマごとの開発（例: `dev_calendar-panel-fix`） | 作業コミット。マージ後は削除してよい |

**フロー**

1. テーマごとに `dev_<name>` を **`main` から**作成して開発（未リリースの `test` 上の変更に依存するときだけ `test` から切る）
2. 区切りがついたら **`dev_*` → `test` の PR を squash マージ**する。ローカルで `git merge` しない
3. `test` で動作確認できたら **`test` → `main` の PR** を作り、**squash マージ**する（`dev_*` から `main` へは出さない）
4. **`main` マージ直後**に `test` を新しい `main` へ合わせる。通常は CI（`sync-test-to-main.yml`）が `reset --hard` 相当の force-with-lease push をする。失敗したときだけ手動:

```bash
git fetch origin
git checkout test
git reset --hard origin/main
git push --force-with-lease origin test
```

`test` の force-push は **このリリース後同期だけ**。開発中の `test` は squash PR のみで進め、merge commit は入れない。`test` にブランチ保護を付ける場合は、Actions の force-push を許可する。

`dev_release-*` は使わない。`main` への PR 元は **`test` のみ**。
