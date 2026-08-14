"""キーボードショートカットのコード正規化（Win32 非依存）."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_NEW_CARD_SHORTCUT = "Ctrl+Shift+N"

_MODIFIER_ORDER = ("Ctrl", "Alt", "Shift")
_MODIFIER_ALIASES = {
    "ctrl": "Ctrl",
    "control": "Ctrl",
    "alt": "Alt",
    "shift": "Shift",
}

_VK_A = 0x41
_VK_0 = 0x30
_VK_F1 = 0x70
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000

# Tk event.state bits（Windows / 共通）
_TK_SHIFT = 0x0001
_TK_CONTROL = 0x0004
_TK_ALT_MASKS = (0x0008, 0x20000)

_IGNORED_KEYSYMS = {
    "Shift_L",
    "Shift_R",
    "Control_L",
    "Control_R",
    "Alt_L",
    "Alt_R",
    "Meta_L",
    "Meta_R",
    "Win_L",
    "Win_R",
    "Caps_Lock",
    "Num_Lock",
    "Scroll_Lock",
}


@dataclass(frozen=True)
class ShortcutChord:
    """修飾キー + 1 キーのショートカット."""

    ctrl: bool
    alt: bool
    shift: bool
    key: str

    def format(self) -> str:
        flags = {"Ctrl": self.ctrl, "Alt": self.alt, "Shift": self.shift}
        parts = [name for name in _MODIFIER_ORDER if flags[name]]
        parts.append(self.key)
        return "+".join(parts)

    def win_modifiers(self) -> int:
        modifiers = 0
        if self.alt:
            modifiers |= MOD_ALT
        if self.ctrl:
            modifiers |= MOD_CONTROL
        if self.shift:
            modifiers |= MOD_SHIFT
        return modifiers | MOD_NOREPEAT

    def virtual_key(self) -> int:
        if len(self.key) == 1 and "A" <= self.key <= "Z":
            return _VK_A + (ord(self.key) - ord("A"))
        if len(self.key) == 1 and "0" <= self.key <= "9":
            return _VK_0 + (ord(self.key) - ord("0"))
        if self.key.startswith("F") and self.key[1:].isdigit():
            index = int(self.key[1:])
            if 1 <= index <= 12:
                return _VK_F1 + (index - 1)
        msg = f"未対応のキーです: {self.key}"
        raise ValueError(msg)

    def has_modifier(self) -> bool:
        return self.ctrl or self.alt or self.shift


def parse_shortcut(text: str | None) -> ShortcutChord | None:
    """正規形のショートカット文字列を解析する。不正なら None。"""
    if text is None:
        return None
    tokens = [token.strip() for token in text.split("+") if token.strip()]
    if len(tokens) < 2:
        return None

    ctrl = alt = shift = False
    key_token: str | None = None
    for token in tokens:
        modifier = _MODIFIER_ALIASES.get(token.lower())
        if modifier == "Ctrl":
            ctrl = True
            continue
        if modifier == "Alt":
            alt = True
            continue
        if modifier == "Shift":
            shift = True
            continue
        if key_token is not None:
            return None
        key_token = token

    if key_token is None or not (ctrl or alt or shift):
        return None
    key = _normalize_key(key_token)
    if key is None:
        return None
    return ShortcutChord(ctrl=ctrl, alt=alt, shift=shift, key=key)


def normalize_shortcut(text: str | None) -> str:
    """不正・欠損時は既定 Ctrl+Shift+N。"""
    chord = parse_shortcut(text)
    if chord is None:
        return DEFAULT_NEW_CARD_SHORTCUT
    return chord.format()


def chord_from_tk_key(keysym: str, state: int) -> ShortcutChord | None:
    """Tk KeyPress からコードを組み立てる。Escape・修飾のみは None。"""
    if keysym == "Escape" or keysym in _IGNORED_KEYSYMS:
        return None
    key = _normalize_key(keysym)
    if key is None:
        return None
    chord = ShortcutChord(
        ctrl=bool(state & _TK_CONTROL),
        alt=any(state & mask for mask in _TK_ALT_MASKS),
        shift=bool(state & _TK_SHIFT),
        key=key,
    )
    if not chord.has_modifier():
        return None
    return chord


def _normalize_key(token: str) -> str | None:
    if len(token) == 1:
        char = token.upper()
        if "A" <= char <= "Z" or "0" <= char <= "9":
            return char
        return None
    upper = token.upper()
    if upper.startswith("F") and upper[1:].isdigit():
        index = int(upper[1:])
        if 1 <= index <= 12:
            return f"F{index}"
    return None
