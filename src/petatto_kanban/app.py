"""Tkinter ベースの GUI アプリケーション（オーバーレイモード）."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, simpledialog, ttk

from petatto_kanban.display import list_monitors, load_display_settings, save_display_settings
from petatto_kanban.display.desktop import TRANSPARENT_COLOR
from petatto_kanban.display.monitors import Monitor, get_monitor, monitor_index_for_name
from petatto_kanban.display.overlay import apply_overlay_mode
from petatto_kanban.models import Card
from petatto_kanban.storage import load_board, save_board

APP_TITLE = "Petatto-Kanban"
CARD_BG = "#fffef8"
CARD_FG = "#222222"
CARD_DESC_FG = "#555555"
CARD_ACTIVE_BG = "#e8e8e0"
CARD_WIDTH = 220
TOOLBAR_BG = "#f0f0f0"
DEFAULT_CARD_X = 120
DEFAULT_CARD_Y = 120
CARD_LABEL_WRAP = 200


@dataclass(frozen=True)
class SettingsDialogResult:
    """設定ダイアログの確定値."""

    confirm_delete: bool
    monitor_index: int


class KanbanApp:
    """オーバーレイ上の自由配置カンバン."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.board = load_board()
        self.display_settings = load_display_settings()
        self._card_widgets: dict[str, tk.Frame] = {}
        self._drag_state: dict[int, tuple[int, int]] = {}
        self._monitors = list_monitors()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.configure(bg=TRANSPARENT_COLOR)

        self._build_toolbar()
        self._apply_overlay_mode()
        self.refresh()

    def _apply_overlay_mode(self) -> None:
        monitor = get_monitor(self.display_settings.monitor_index)
        apply_overlay_mode(self.root, monitor)
        self.toolbar.place(x=monitor.width - 16, y=16, anchor=tk.NE)

    def _lift_ui(self) -> None:
        """カードの上にツールバーが来るよう Z 順を整える."""
        for frame in self._card_widgets.values():
            frame.lift()
        self.toolbar.lift()

    def _build_toolbar(self) -> None:
        self.toolbar = tk.Frame(
            self.root,
            bg=TOOLBAR_BG,
            bd=1,
            relief=tk.RIDGE,
            padx=4,
            pady=4,
        )
        ttk.Button(self.toolbar, text="×", width=3, command=self._on_close).pack(
            side=tk.RIGHT,
            padx=2,
        )
        ttk.Button(self.toolbar, text="設定", command=self._open_settings).pack(
            side=tk.RIGHT,
            padx=2,
        )
        ttk.Button(self.toolbar, text="+ カード", command=self._add_card).pack(
            side=tk.RIGHT,
            padx=2,
        )

    def refresh(self) -> None:
        """カードを再描画する."""
        for widget in self._card_widgets.values():
            widget.destroy()
        self._card_widgets.clear()
        self._drag_state.clear()

        for card in self.board.cards:
            self._render_card(card)
        self._lift_ui()

    def _render_card(self, card: Card) -> None:
        frame = tk.Frame(
            self.root,
            bg=CARD_BG,
            bd=1,
            relief=tk.RIDGE,
            padx=8,
            pady=8,
            highlightthickness=0,
        )
        frame.place(x=card.x, y=card.y)
        self._card_widgets[card.id] = frame

        self._card_label(
            frame,
            text=card.title,
            font=("Segoe UI", 10, "bold"),
            fg=CARD_FG,
        ).pack(anchor=tk.W, fill=tk.X)

        if card.description:
            self._card_label(
                frame,
                text=card.description,
                fg=CARD_DESC_FG,
            ).pack(anchor=tk.W, pady=(4, 0), fill=tk.X)

        edit_btn = self._card_button(frame, "編集", width=6, command=lambda: self._edit_card(card))
        edit_btn.pack(anchor=tk.W, pady=(8, 0))

        self._finalize_card_frame(frame)
        self._bind_card_interactions(frame, card, skip_drag={edit_btn})

    def _card_label(self, parent: tk.Misc, **kwargs) -> tk.Label:
        defaults = {
            "bg": CARD_BG,
            "wraplength": CARD_LABEL_WRAP,
            "justify": tk.LEFT,
            "anchor": tk.W,
        }
        defaults.update(kwargs)
        return tk.Label(parent, **defaults)

    def _card_button(self, parent: tk.Misc, text: str, command, **kwargs) -> tk.Button:
        options = {
            "text": text,
            "bg": CARD_BG,
            "fg": CARD_FG,
            "activebackground": CARD_ACTIVE_BG,
            "activeforeground": CARD_FG,
            "relief": tk.RAISED,
            "bd": 1,
            "command": command,
        }
        options.update(kwargs)
        return tk.Button(parent, **options)

    def _finalize_card_frame(self, frame: tk.Frame) -> None:
        frame.update_idletasks()
        frame.config(
            width=max(CARD_WIDTH, frame.winfo_reqwidth()),
            height=frame.winfo_reqheight(),
        )
        frame.pack_propagate(False)

    def _bind_card_interactions(
        self,
        frame: tk.Frame,
        card: Card,
        *,
        skip_drag: set[tk.Misc],
    ) -> None:
        def on_delete(_event: tk.Event) -> None:
            self._delete_card(card)

        for widget in (frame, *frame.winfo_children()):
            widget.bind("<ButtonRelease-3>", on_delete)
            if widget in skip_drag:
                continue
            widget.bind("<Button-1>", lambda e, f=frame: self._start_drag(e, f))
            widget.bind("<B1-Motion>", lambda e, c=card, f=frame: self._on_drag(e, c, f))
            widget.bind("<ButtonRelease-1>", lambda _e, c=card: self._end_drag(c))

    def _default_card_position(self) -> tuple[int, int]:
        index = len(self.board.cards)
        return (
            DEFAULT_CARD_X + (index % 4) * 32,
            DEFAULT_CARD_Y + (index // 4) * 32,
        )

    def _start_drag(self, event: tk.Event, frame: tk.Frame) -> None:
        self._drag_state[frame.winfo_id()] = (event.x, event.y)

    def _on_drag(self, event: tk.Event, card: Card, frame: tk.Frame) -> None:
        origin = self._drag_state.get(frame.winfo_id())
        if origin is None:
            return
        new_x = frame.winfo_x() + event.x - origin[0]
        new_y = frame.winfo_y() + event.y - origin[1]
        frame.place(x=new_x, y=new_y)
        card.x = new_x
        card.y = new_y

    def _end_drag(self, card: Card) -> None:
        card.touch()
        save_board(self.board)

    def _add_card(self) -> None:
        title = simpledialog.askstring(
            "カード追加",
            "タイトルを入力してください:",
            parent=self.root,
        )
        if not title or not title.strip():
            return

        card_x, card_y = self._default_card_position()
        self.board.cards.append(Card(title=title.strip(), x=card_x, y=card_y))
        self._persist_and_refresh()

    def _edit_card(self, card: Card) -> None:
        dialog = _CardEditDialog(self.root, card.title, card.description)
        if dialog.result is None:
            return

        title, description = dialog.result
        if not title.strip():
            messagebox.showwarning(APP_TITLE, "タイトルは空にできません。", parent=self.root)
            return

        card.title = title.strip()
        card.description = description.strip()
        card.touch()
        self._persist_and_refresh()

    def _delete_card(self, card: Card) -> None:
        if self.display_settings.confirm_delete and not messagebox.askyesno(
            APP_TITLE,
            f"「{card.title}」を削除しますか？",
            parent=self.root,
        ):
            return

        self.board.remove_card(card.id)
        self._persist_and_refresh()

    def _open_settings(self) -> None:
        dialog = _SettingsDialog(
            self.root,
            confirm_delete=self.display_settings.confirm_delete,
            monitor_index=self.display_settings.monitor_index,
            monitors=self._monitors,
        )
        if dialog.result is None:
            return

        self._apply_settings(dialog.result)
        messagebox.showinfo(APP_TITLE, "設定を保存しました。", parent=self.root)

    def _apply_settings(self, settings: SettingsDialogResult) -> None:
        monitor_changed = settings.monitor_index != self.display_settings.monitor_index
        self.display_settings.confirm_delete = settings.confirm_delete
        self.display_settings.monitor_index = settings.monitor_index
        save_display_settings(self.display_settings)

        if monitor_changed:
            self._apply_overlay_mode()
            self.refresh()

    def _persist_and_refresh(self) -> None:
        save_board(self.board)
        self.refresh()

    def _on_close(self) -> None:
        save_board(self.board)
        save_display_settings(self.display_settings)
        self.root.destroy()


class _CardEditDialog(simpledialog.Dialog):
    """カード編集ダイアログ."""

    def __init__(self, parent: tk.Misc, title: str, description: str) -> None:
        self._initial_title = title
        self._initial_description = description
        self.result: tuple[str, str] | None = None
        super().__init__(parent, title="カード編集")

    def body(self, master: tk.Misc) -> tk.Widget:
        ttk.Label(master, text="タイトル").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        self.title_entry = ttk.Entry(master, width=40)
        self.title_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 8))
        self.title_entry.insert(0, self._initial_title)

        ttk.Label(master, text="説明").grid(row=2, column=0, sticky=tk.W, pady=(0, 4))
        self.description_text = tk.Text(master, width=40, height=5, wrap=tk.WORD)
        self.description_text.grid(row=3, column=0, sticky=tk.EW)
        self.description_text.insert("1.0", self._initial_description)
        master.columnconfigure(0, weight=1)
        return self.title_entry

    def apply(self) -> None:
        title = self.title_entry.get()
        description = self.description_text.get("1.0", tk.END)
        self.result = (title, description)


class _SettingsDialog(simpledialog.Dialog):
    """アプリ設定ダイアログ."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        confirm_delete: bool,
        monitor_index: int,
        monitors: list[Monitor],
    ) -> None:
        self._confirm_delete = confirm_delete
        self._monitor_index = monitor_index
        self._monitors = monitors
        self.result: SettingsDialogResult | None = None
        super().__init__(parent, title="設定")

    def body(self, master: tk.Misc) -> tk.Widget:
        ttk.Label(master, text="表示ディスプレイ").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        monitor_names = [monitor.name for monitor in self._monitors]
        default_name = monitor_names[min(self._monitor_index, len(monitor_names) - 1)]
        self.monitor_var = tk.StringVar(value=default_name)
        self.monitor_menu = ttk.Combobox(
            master,
            textvariable=self.monitor_var,
            values=monitor_names,
            state="readonly",
            width=28,
        )
        self.monitor_menu.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

        self.confirm_var = tk.BooleanVar(value=self._confirm_delete)
        ttk.Checkbutton(
            master,
            text="カード削除時に確認ダイアログを表示する",
            variable=self.confirm_var,
        ).grid(row=2, column=0, sticky=tk.W)
        master.columnconfigure(0, weight=1)
        return self.monitor_menu

    def apply(self) -> None:
        self.result = SettingsDialogResult(
            confirm_delete=self.confirm_var.get(),
            monitor_index=monitor_index_for_name(
                self._monitors,
                self.monitor_var.get(),
                self._monitor_index,
            ),
        )


def run_app() -> None:
    """アプリケーションを起動する."""
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    KanbanApp(root)
    root.mainloop()
