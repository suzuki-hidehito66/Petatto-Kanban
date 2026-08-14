"""auto_start のテスト."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from petatto_kanban.system import auto_start


@dataclass
class FakeWinReg:
    """winreg 互換のインメモリ実装."""

    values: dict[str, str] = field(default_factory=dict)
    HKEY_CURRENT_USER: object = object()
    KEY_READ: int = 1
    KEY_SET_VALUE: int = 2
    REG_SZ: int = 1
    create_called: bool = False
    missing_key: bool = False

    def OpenKey(self, key: object, sub_key: str, *, reserved: int = 0, access: int = 0) -> object:
        assert key is self.HKEY_CURRENT_USER
        assert sub_key == auto_start.REGISTRY_RUN_KEY
        if self.missing_key:
            msg = "missing key"
            raise OSError(msg)
        return key

    def CreateKeyEx(
        self, key: object, sub_key: str, reserved: int = 0, access: int = 0
    ) -> object:
        self.create_called = True
        self.missing_key = False
        return self.OpenKey(key, sub_key, reserved=reserved, access=access)

    def QueryValueEx(self, key: object, name: str) -> tuple[object, int]:
        if name not in self.values:
            msg = "missing"
            raise OSError(msg)
        return self.values[name], self.REG_SZ

    def SetValueEx(
        self,
        key: object,
        name: str,
        reserved: int,
        reg_type: int,
        value: str,
    ) -> None:
        assert reg_type == self.REG_SZ
        self.values[name] = value

    def DeleteValue(self, key: object, name: str) -> None:
        if name not in self.values:
            msg = "missing"
            raise OSError(msg)
        del self.values[name]

    def CloseKey(self, key: object) -> None:
        return None


def test_is_auto_start_supported_on_linux() -> None:
    assert auto_start.is_auto_start_supported() is False


def test_apply_auto_start_noop_when_unsupported() -> None:
    auto_start.apply_auto_start_setting(True)


def test_apply_auto_start_enable_creates_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auto_start, "is_auto_start_supported", lambda: True)
    reg = FakeWinReg(missing_key=True)
    exe_command = r'"C:\Apps\Petatto-Kanban.exe"'
    monkeypatch.setattr(auto_start, "resolve_launch_command", lambda: exe_command)

    auto_start.apply_auto_start_setting(True, winreg_module=reg)

    assert reg.create_called is True
    assert reg.values[auto_start.REGISTRY_VALUE_NAME] == exe_command


def test_apply_auto_start_enable_and_disable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auto_start, "is_auto_start_supported", lambda: True)
    reg = FakeWinReg()
    exe_command = r'"C:\Apps\Petatto-Kanban.exe"'
    monkeypatch.setattr(auto_start, "resolve_launch_command", lambda: exe_command)

    auto_start.apply_auto_start_setting(True, winreg_module=reg)
    assert reg.values[auto_start.REGISTRY_VALUE_NAME] == exe_command

    auto_start.apply_auto_start_setting(False, winreg_module=reg)
    assert auto_start.REGISTRY_VALUE_NAME not in reg.values


def test_apply_auto_start_disable_when_unregistered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auto_start, "is_auto_start_supported", lambda: True)
    reg = FakeWinReg()
    auto_start.apply_auto_start_setting(False, winreg_module=reg)
    assert reg.values == {}


def test_sync_auto_start_from_settings_skips_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(auto_start, "is_auto_start_supported", lambda: True)
    called: list[bool] = []

    def capture(enabled: bool, **_kwargs: object) -> None:
        called.append(enabled)

    monkeypatch.setattr(auto_start, "apply_auto_start_setting", capture)
    auto_start.sync_auto_start_from_settings(False)
    assert called == []


def test_sync_auto_start_from_settings_registers_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(auto_start, "is_auto_start_supported", lambda: True)
    reg = FakeWinReg()
    monkeypatch.setattr(
        auto_start,
        "resolve_launch_command",
        lambda: r'"C:\Apps\Petatto-Kanban.exe"',
    )
    auto_start.sync_auto_start_from_settings(True, winreg_module=reg)
    assert auto_start.REGISTRY_VALUE_NAME in reg.values


def test_is_auto_start_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auto_start, "is_auto_start_supported", lambda: True)
    reg = FakeWinReg()
    assert auto_start.is_auto_start_registered(winreg_module=reg) is False
    reg.values[auto_start.REGISTRY_VALUE_NAME] = r'"C:\Apps\Petatto-Kanban.exe"'
    assert auto_start.is_auto_start_registered(winreg_module=reg) is True
