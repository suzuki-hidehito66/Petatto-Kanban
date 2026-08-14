"""マウスボタン押下の判定（Windows）。"""

from __future__ import annotations

from petatto_kanban.display.transparent import is_windows

VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_XBUTTON1 = 0x05
VK_XBUTTON2 = 0x06
_MOUSE_BUTTON_VKS = (VK_LBUTTON, VK_RBUTTON, VK_MBUTTON, VK_XBUTTON1, VK_XBUTTON2)
_KEY_DOWN_MASK = 0x8000


def is_any_mouse_button_down() -> bool:
    """いずれかのマウスボタンが押下中なら True（非 Windows は常に False）。"""
    if not is_windows():
        return False

    from petatto_kanban.display.win32_user32 import async_key_state

    return any(
        async_key_state(virtual_key) & _KEY_DOWN_MASK
        for virtual_key in _MOUSE_BUTTON_VKS
    )
