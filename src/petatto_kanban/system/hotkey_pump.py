"""Win32 ホットキー受信ポンプ（専用スレッド + ネイティブ DefWindowProc）.

Tk のメッセージポンプ上で Python ctypes WndProc を呼ぶと、Python 3.14 で
thread state が NULL のまま PyEval_RestoreThread され致命エラーになる。
このモジュールは Tk とは別スレッドでメッセージ専用ウィンドウを回し、
WndProc は user32 の DefWindowProcW だけを使う。
"""

from __future__ import annotations

import ctypes
import queue
import threading
from ctypes import wintypes
from dataclasses import dataclass, field
from typing import Protocol

HWND_MESSAGE = -3
WM_QUIT = 0x0012
WM_APP = 0x8000
WM_HOTKEY = 0x0312
_COMMAND_WAIT_SECONDS = 5.0
_THREAD_START_SECONDS = 5.0
_THREAD_JOIN_SECONDS = 2.0


class HotkeyRegistrar(Protocol):
    """RegisterHotKey 互換."""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None: ...

    def unregister(self, hwnd: int, hotkey_id: int) -> None: ...


class Win32HotkeyRegistrar:
    """user32 RegisterHotKey / UnregisterHotKey."""

    def register(self, hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None:
        user32 = _user32()
        if not user32.RegisterHotKey(hwnd, hotkey_id, modifiers, vk):
            raise ctypes.WinError()

    def unregister(self, hwnd: int, hotkey_id: int) -> None:
        _user32().UnregisterHotKey(hwnd, hotkey_id)


@dataclass
class _PumpCommand:
    kind: str
    hotkey_id: int
    modifiers: int = 0
    vk: int = 0
    done: threading.Event = field(default_factory=threading.Event)
    errors: list[BaseException] = field(default_factory=list)


class Win32HotkeyPump:
    """専用スレッドでメッセージ専用ウィンドウを回す（Python WndProc なし）."""

    def __init__(self, *, registrar: HotkeyRegistrar | None = None) -> None:
        self._registrar = registrar or Win32HotkeyRegistrar()
        self._commands: queue.Queue[_PumpCommand] = queue.Queue()
        self._fired: queue.SimpleQueue[int] = queue.SimpleQueue()
        self._ready = threading.Event()
        self._start_error: BaseException | None = None
        self._hwnd = 0
        self._thread_id = 0
        self._class_name = ""
        self._hinstance: int | None = None
        self._active_ids: set[int] = set()
        self._closed = False
        self._thread = threading.Thread(
            target=self._run,
            name="petatto-hotkey",
            daemon=True,
        )

    def start(self) -> None:
        self._thread.start()
        if not self._ready.wait(timeout=_THREAD_START_SECONDS):
            self.close()
            msg = "ホットキー用スレッドの起動がタイムアウトしました"
            raise RuntimeError(msg)
        if self._start_error is not None:
            self._thread.join(timeout=_THREAD_JOIN_SECONDS)
            raise self._start_error

    def set_hotkey(self, hotkey_id: int, modifiers: int, vk: int) -> None:
        self._submit(
            _PumpCommand(kind="bind", hotkey_id=hotkey_id, modifiers=modifiers, vk=vk)
        )

    def clear_hotkey(self, hotkey_id: int) -> None:
        self._submit(_PumpCommand(kind="unbind", hotkey_id=hotkey_id))

    def drain(self) -> list[int]:
        ids: list[int] = []
        while True:
            try:
                ids.append(self._fired.get_nowait())
            except queue.Empty:
                return ids

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        thread_id = self._thread_id
        if thread_id:
            _user32().PostThreadMessageW(thread_id, WM_QUIT, 0, 0)
        if self._thread.is_alive():
            self._thread.join(timeout=_THREAD_JOIN_SECONDS)

    def _submit(self, command: _PumpCommand) -> None:
        if self._closed or self._hwnd == 0:
            msg = "ホットキー用スレッドが停止しています"
            raise RuntimeError(msg)
        self._commands.put(command)
        if not _user32().PostMessageW(self._hwnd, WM_APP, 0, 0):
            raise ctypes.WinError()
        if not command.done.wait(timeout=_COMMAND_WAIT_SECONDS):
            msg = "ホットキー用スレッドが応答しません"
            raise RuntimeError(msg)
        if command.errors:
            raise command.errors[0]

    def _run(self) -> None:
        try:
            self._create_window()
            _, kernel32 = _window_apis()
            self._thread_id = int(kernel32.GetCurrentThreadId())
        except (OSError, RuntimeError) as error:
            self._start_error = error
            self._ready.set()
            return
        self._ready.set()
        user32 = _user32()
        msg = _MSG()
        while True:
            status = int(user32.GetMessageW(ctypes.byref(msg), None, 0, 0))
            if status <= 0:
                break
            if msg.message == WM_HOTKEY:
                self._fired.put(int(msg.wParam))
                continue
            if msg.message == WM_APP:
                self._process_commands()
                continue
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        self._destroy_window()

    def _process_commands(self) -> None:
        while True:
            try:
                command = self._commands.get_nowait()
            except queue.Empty:
                return
            try:
                if command.kind == "bind":
                    self._unbind(command.hotkey_id)
                    self._registrar.register(
                        self._hwnd,
                        command.hotkey_id,
                        command.modifiers,
                        command.vk,
                    )
                    self._active_ids.add(command.hotkey_id)
                elif command.kind == "unbind":
                    self._unbind(command.hotkey_id)
            except (OSError, RuntimeError) as error:
                command.errors.append(error)
            finally:
                command.done.set()

    def _unbind(self, hotkey_id: int) -> None:
        self._registrar.unregister(self._hwnd, hotkey_id)
        self._active_ids.discard(hotkey_id)

    def _create_window(self) -> None:
        user32, kernel32 = _window_apis()
        hinstance = kernel32.GetModuleHandleW(None)
        self._hinstance = int(hinstance) if hinstance else None
        self._class_name = f"PetattoKanbanHotkey_{id(self)}"
        def_wnd_proc = kernel32.GetProcAddress(
            kernel32.GetModuleHandleW("user32"),
            b"DefWindowProcW",
        )
        if not def_wnd_proc:
            raise ctypes.WinError()
        window_class = _WNDCLASSW()
        window_class.lpfnWndProc = def_wnd_proc
        window_class.hInstance = hinstance
        window_class.lpszClassName = self._class_name
        if not user32.RegisterClassW(ctypes.byref(window_class)):
            raise ctypes.WinError()
        hwnd = user32.CreateWindowExW(
            0,
            self._class_name,
            None,
            0,
            0,
            0,
            0,
            0,
            HWND_MESSAGE,
            None,
            hinstance,
            None,
        )
        if not hwnd:
            user32.UnregisterClassW(self._class_name, hinstance)
            raise ctypes.WinError()
        self._hwnd = int(hwnd)

    def _destroy_window(self) -> None:
        if self._hwnd == 0:
            return
        user32 = _user32()
        for hotkey_id in list(self._active_ids):
            self._unbind(hotkey_id)
        user32.DestroyWindow(self._hwnd)
        if self._hinstance is not None and self._class_name:
            user32.UnregisterClassW(self._class_name, self._hinstance)
        self._hwnd = 0
        self._hinstance = None


class _POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class _MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", _POINT),
    ]


class _WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", ctypes.c_uint),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.c_void_p),
        ("hIcon", ctypes.c_void_p),
        ("hCursor", ctypes.c_void_p),
        ("hbrBackground", ctypes.c_void_p),
        ("lpszMenuName", ctypes.c_wchar_p),
        ("lpszClassName", ctypes.c_wchar_p),
    ]


def _user32() -> object:
    user32 = ctypes.windll.user32
    user32.RegisterHotKey.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.c_uint,
    ]
    user32.RegisterHotKey.restype = ctypes.c_int
    user32.UnregisterHotKey.argtypes = [ctypes.c_void_p, ctypes.c_int]
    user32.UnregisterHotKey.restype = ctypes.c_int
    user32.PostMessageW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
    ]
    user32.PostMessageW.restype = ctypes.c_int
    user32.PostThreadMessageW.argtypes = [
        wintypes.DWORD,
        ctypes.c_uint,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
    ]
    user32.PostThreadMessageW.restype = ctypes.c_int
    user32.GetMessageW.argtypes = [
        ctypes.POINTER(_MSG),
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_uint,
    ]
    user32.GetMessageW.restype = ctypes.c_int
    user32.TranslateMessage.argtypes = [ctypes.POINTER(_MSG)]
    user32.TranslateMessage.restype = ctypes.c_int
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(_MSG)]
    user32.DispatchMessageW.restype = ctypes.c_ssize_t
    user32.DestroyWindow.argtypes = [ctypes.c_void_p]
    user32.DestroyWindow.restype = ctypes.c_int
    user32.UnregisterClassW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p]
    user32.UnregisterClassW.restype = ctypes.c_int
    return user32


def _window_apis() -> tuple[object, object]:
    user32 = _user32()
    user32.RegisterClassW.argtypes = [ctypes.POINTER(_WNDCLASSW)]
    user32.RegisterClassW.restype = ctypes.c_ushort
    user32.CreateWindowExW.argtypes = [
        ctypes.c_uint,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_uint,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    user32.CreateWindowExW.restype = ctypes.c_void_p
    kernel32 = ctypes.windll.kernel32
    kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
    kernel32.GetModuleHandleW.restype = ctypes.c_void_p
    kernel32.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    kernel32.GetProcAddress.restype = ctypes.c_void_p
    kernel32.GetCurrentThreadId.argtypes = []
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    return user32, kernel32
