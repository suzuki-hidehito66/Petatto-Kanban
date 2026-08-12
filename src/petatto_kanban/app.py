"""Tkinter ベースの GUI アプリケーション."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from petatto_kanban.display import (
    list_monitors,
    load_display_settings,
    save_display_settings,
)
from petatto_kanban.display.desktop import TRANSPARENT_COLOR, apply_desktop_mode
from petatto_kanban.display.monitors import get_monitor
from petatto_kanban.display.settings import DisplayMode
from petatto_kanban.models import Card, Column
from petatto_kanban.storage import load_board, save_board

APP_TITLE = "Petatto-Kanban"
WINDOW_MIN_WIDTH = 960
WINDOW_MIN_HEIGHT = 540
PANEL_BG = "#f5f5f5"


class KanbanApp:
    """カンバンボード GUI."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.board = load_board()
        self.display_settings = load_display_settings()
        self._card_widgets: dict[str, tk.Frame] = {}
        self._monitors = list_monitors()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        if self.display_settings.mode == DisplayMode.DESKTOP:
            self.root.configure(bg=TRANSPARENT_COLOR)
            self.main_panel = tk.Frame(self.root, bg=PANEL_BG, bd=1, relief=tk.RIDGE)
            self.main_panel.pack(anchor=tk.NW, padx=24, pady=24)
        else:
            self.root.title(APP_TITLE)
            self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
            self.main_panel = tk.Frame(self.root, bg=PANEL_BG)
            self.main_panel.pack(fill=tk.BOTH, expand=True)

        self._build_header()
        self._build_board_area()
        self.refresh()
        self._apply_display_mode()

    def _apply_display_mode(self) -> None:
        """表示設定に従いデスクトップモード等を適用する."""
        if self.display_settings.mode != DisplayMode.DESKTOP:
            return

        monitor = get_monitor(self.display_settings.monitor_index)
        apply_desktop_mode(self.root, monitor)

    def _build_header(self) -> None:
        header = ttk.Frame(self.main_panel, padding=(12, 8))
        header.pack(fill=tk.X)

        ttk.Label(header, text=self.board.name, font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

        monitor_names = [monitor.name for monitor in self._monitors]
        self.monitor_var = tk.StringVar(
            value=monitor_names[min(self.display_settings.monitor_index, len(monitor_names) - 1)]
        )
        self.monitor_menu = ttk.Combobox(
            header,
            textvariable=self.monitor_var,
            values=monitor_names,
            state="readonly",
            width=14,
        )
        self.monitor_menu.pack(side=tk.RIGHT, padx=(8, 0))
        self.monitor_menu.bind("<<ComboboxSelected>>", self._on_monitor_changed)

        ttk.Label(header, text="ディスプレイ:").pack(side=tk.RIGHT)

        ttk.Button(header, text="再読み込み", command=self._reload).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(header, text="保存", command=self._save).pack(side=tk.RIGHT)

    def _on_monitor_changed(self, _event: object = None) -> None:
        selected = self.monitor_var.get()
        for monitor in self._monitors:
            if monitor.name == selected:
                self.display_settings.monitor_index = monitor.index
                save_display_settings(self.display_settings)
                self._apply_display_mode()
                break

    def _build_board_area(self) -> None:
        container = ttk.Frame(self.main_panel, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        self.columns_frame = ttk.Frame(container)
        self.columns_frame.pack(fill=tk.BOTH, expand=True)

    def refresh(self) -> None:
        """列とカード表示を再描画する."""
        for child in self.columns_frame.winfo_children():
            child.destroy()
        self._card_widgets.clear()

        for index, column in enumerate(self.board.columns):
            self.columns_frame.columnconfigure(index, weight=1, uniform="columns")
            self._render_column(index, column)

    def _render_column(self, index: int, column: Column) -> None:
        frame = ttk.LabelFrame(self.columns_frame, text=column.name, padding=8)
        frame.grid(row=0, column=index, sticky="nsew", padx=4)
        frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(frame, highlightthickness=0, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        cards_container = ttk.Frame(canvas)

        cards_container.bind(
            "<Configure>",
            lambda _event, target=canvas: target.configure(scrollregion=target.bbox("all")),
        )
        canvas.create_window((0, 0), window=cards_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        sorted_cards = sorted(column.cards, key=lambda card: card.order)
        for card in sorted_cards:
            self._render_card(cards_container, column, card)

        ttk.Button(
            frame,
            text="+ カードを追加",
            command=lambda col=column: self._add_card(col),
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _render_card(self, parent: ttk.Frame, column: Column, card: Card) -> None:
        card_frame = ttk.Frame(parent, padding=8, relief=tk.GROOVE, borderwidth=1)
        card_frame.pack(fill=tk.X, pady=4, padx=2)
        self._card_widgets[card.id] = card_frame

        ttk.Label(card_frame, text=card.title, font=("Segoe UI", 10, "bold"), wraplength=220).pack(
            anchor=tk.W
        )
        if card.description:
            ttk.Label(
                card_frame,
                text=card.description,
                wraplength=220,
                foreground="#555555",
            ).pack(anchor=tk.W, pady=(4, 0))

        actions = ttk.Frame(card_frame)
        actions.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(
            actions,
            text="編集",
            width=6,
            command=lambda c=card: self._edit_card(c),
        ).pack(side=tk.LEFT)

        move_menu = ttk.Combobox(
            actions,
            values=[col.name for col in self.board.columns if col.id != column.id],
            state="readonly",
            width=12,
        )
        move_menu.set("移動先...")
        move_menu.pack(side=tk.LEFT, padx=(4, 0))
        move_menu.bind(
            "<<ComboboxSelected>>",
            lambda _event, c=card, src=column, menu=move_menu: self._move_card(c, src, menu),
        )

        ttk.Button(
            actions,
            text="削除",
            width=6,
            command=lambda c=card, col=column: self._delete_card(c, col),
        ).pack(side=tk.RIGHT)

    def _add_card(self, column: Column) -> None:
        title = simpledialog.askstring(
            "カード追加",
            "タイトルを入力してください:",
            parent=self.root,
        )
        if not title or not title.strip():
            return

        card = Card(title=title.strip(), order=len(column.cards))
        column.cards.append(card)
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

    def _move_card(self, card: Card, source: Column, menu: ttk.Combobox) -> None:
        destination_name = menu.get()
        menu.set("移動先...")
        destination = next(
            (col for col in self.board.columns if col.name == destination_name),
            None,
        )
        if destination is None or destination.id == source.id:
            return

        source.cards = [item for item in source.cards if item.id != card.id]
        card.order = len(destination.cards)
        destination.cards.append(card)
        card.touch()
        self._normalize_orders(source)
        self._normalize_orders(destination)
        self._persist_and_refresh()

    def _delete_card(self, card: Card, column: Column) -> None:
        confirmed = messagebox.askyesno(
            APP_TITLE,
            f"「{card.title}」を削除しますか？",
            parent=self.root,
        )
        if not confirmed:
            return

        column.cards = [item for item in column.cards if item.id != card.id]
        self._normalize_orders(column)
        self._persist_and_refresh()

    def _normalize_orders(self, column: Column) -> None:
        for index, card in enumerate(sorted(column.cards, key=lambda item: item.order)):
            card.order = index

    def _persist_and_refresh(self) -> None:
        save_board(self.board)
        self.refresh()

    def _save(self) -> None:
        save_board(self.board)
        save_display_settings(self.display_settings)
        messagebox.showinfo(APP_TITLE, "保存しました。", parent=self.root)

    def _reload(self) -> None:
        self.board = load_board()
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


def run_app() -> None:
    """アプリケーションを起動する."""
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    KanbanApp(root)
    root.mainloop()
