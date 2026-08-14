"""Windows ログオン時の自動起動（レジストリ Run キー）."""

from __future__ import annotations

import sys
from typing import Protocol

from petatto_kanban.system.launch_command import resolve_launch_command

REGISTRY_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REGISTRY_VALUE_NAME = "Petatto-Kanban"


class WinRegBackend(Protocol):
    """winreg 互換のテスト差し替え用."""

    def OpenKey(
        self, key: object, sub_key: str, *, reserved: int = 0, access: int = 0
    ) -> object: ...

    def CreateKeyEx(
        self, key: object, sub_key: str, reserved: int = 0, access: int = 0
    ) -> object: ...

    def QueryValueEx(self, key: object, name: str) -> tuple[object, int]: ...

    def SetValueEx(
        self, key: object, name: str, reserved: int, reg_type: int, value: str
    ) -> None: ...

    def DeleteValue(self, key: object, name: str) -> None: ...

    def CloseKey(self, key: object) -> None: ...

    @property
    def HKEY_CURRENT_USER(self) -> object: ...

    @property
    def KEY_READ(self) -> int: ...

    @property
    def KEY_SET_VALUE(self) -> int: ...

    @property
    def REG_SZ(self) -> int: ...


def is_auto_start_supported() -> bool:
    """対象 OS（Windows 11 以降）上かどうか。"""
    return sys.platform == "win32"


def is_auto_start_registered(*, winreg_module: WinRegBackend | None = None) -> bool:
    """Run キーに本アプリのエントリがあるか。"""
    if not is_auto_start_supported():
        return False
    reg = _winreg(winreg_module)
    try:
        with _open_run_key(reg, access=reg.KEY_READ, create=False) as key:
            reg.QueryValueEx(key, REGISTRY_VALUE_NAME)
    except OSError:
        return False
    return True


def apply_auto_start_setting(
    enabled: bool,
    *,
    command: str | None = None,
    winreg_module: WinRegBackend | None = None,
) -> None:
    """settings.json の launch_at_login をレジストリに反映する。"""
    if not is_auto_start_supported():
        return

    reg = _winreg(winreg_module)
    if enabled:
        _register_run_value(reg, command=command)
        return
    _unregister_run_value(reg)


def sync_auto_start_from_settings(
    launch_at_login: bool,
    *,
    command: str | None = None,
    winreg_module: WinRegBackend | None = None,
) -> None:
    """起動時・設定保存時に settings とレジストリを一致させる.

    起動時は ``launch_at_login`` が True のときだけ呼び、コマンド行を再書き込みする。
    False のときはレジストリを変更しない（OFF は設定ダイアログ確定時のみ削除）。
    """
    if not launch_at_login:
        return
    apply_auto_start_setting(True, command=command, winreg_module=winreg_module)


def _register_run_value(reg: WinRegBackend, *, command: str | None) -> None:
    launch_command = command or resolve_launch_command()
    if not launch_command.strip():
        msg = "自動起動用の実行パスを解決できません。"
        raise RuntimeError(msg)
    with _open_run_key(reg, access=reg.KEY_SET_VALUE, create=True) as key:
        reg.SetValueEx(key, REGISTRY_VALUE_NAME, 0, reg.REG_SZ, launch_command)


def _unregister_run_value(reg: WinRegBackend) -> None:
    try:
        with _open_run_key(reg, access=reg.KEY_SET_VALUE, create=False) as key:
            reg.DeleteValue(key, REGISTRY_VALUE_NAME)
    except OSError:
        return


def _winreg(winreg_module: WinRegBackend | None) -> WinRegBackend:
    if winreg_module is not None:
        return winreg_module
    import winreg as std_winreg

    return std_winreg  # type: ignore[return-value]


class _RunKey:
    def __init__(self, reg: WinRegBackend, key: object) -> None:
        self._reg = reg
        self._key = key

    def __enter__(self) -> object:
        return self._key

    def __exit__(self, *_args: object) -> None:
        self._reg.CloseKey(self._key)


def _open_run_key(reg: WinRegBackend, *, access: int, create: bool) -> _RunKey:
    if create:
        key = reg.CreateKeyEx(reg.HKEY_CURRENT_USER, REGISTRY_RUN_KEY, 0, access)
    else:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, REGISTRY_RUN_KEY, access=access)
    return _RunKey(reg, key)
