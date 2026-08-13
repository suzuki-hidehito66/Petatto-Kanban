"""カード UI の描画（FR-026 スケール対応）."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from petatto_kanban.card_ui import CardUiRefs
from petatto_kanban.display.ui_metrics import UiMetrics
from petatto_kanban.due_date import due_date_panel_style, format_due_date
from petatto_kanban.models import Card
from petatto_kanban.progress import progress_color

if TYPE_CHECKING:
    from collections.abc import Callable

CARD_BG = "#fffef8"
CARD_FG = "#222222"
CARD_TITLE_FRAME_BD = 1
DUE_PANEL_BD = 1
PROGRESS_TRACK_BG = "#e8e8e8"


class CardRenderer:
    """UiMetrics に基づきカードウィジェットを構築する."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        metrics: UiMetrics,
        on_card_enter: Callable[[tk.Event], None],
        progress_widgets: dict[str, tk.Canvas],
    ) -> None:
        self._parent = parent
        self._metrics = metrics
        self._on_card_enter = on_card_enter
        self._progress_widgets = progress_widgets

    @property
    def metrics(self) -> UiMetrics:
        return self._metrics

    def render(self, card: Card) -> CardUiRefs:
        metrics = self._metrics
        frame = tk.Frame(
            self._parent,
            bg=CARD_BG,
            bd=metrics.card_frame_border,
            relief=tk.RIDGE,
            padx=8,
            pady=8,
            highlightthickness=0,
        )
        frame.place(x=card.x, y=card.y)

        title_frame = tk.Frame(
            frame,
            bg=CARD_BG,
            bd=CARD_TITLE_FRAME_BD,
            relief=tk.GROOVE,
            highlightthickness=0,
            padx=6,
            pady=4,
        )
        title_frame.pack(anchor=tk.NW, fill=tk.X)

        title_label = self._label(
            title_frame,
            text=card.title,
            font=metrics.title_font,
            fg=CARD_FG,
            cursor="xterm",
        )
        title_label.pack(anchor=tk.NW, fill=tk.X)

        due_panel, due_label = self._create_due_date_panel(frame, card)
        due_panel.pack(anchor=tk.NW, fill=tk.X, pady=(4, 0))

        progress_canvas = self._create_progress_canvas(frame, card)
        progress_canvas.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 0))

        self._finalize_frame(frame)
        frame.bind("<Enter>", self._on_card_enter, add="+")
        return CardUiRefs(
            frame=frame,
            title_frame=title_frame,
            title_label=title_label,
            due_panel=due_panel,
            due_label=due_label,
            progress_canvas=progress_canvas,
        )

    def draw_progress(self, canvas: tk.Canvas, progress: int) -> None:
        bar_height = self._metrics.progress_bar_height
        canvas.delete("all")
        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), bar_height)
        canvas.create_rectangle(0, 0, width, height, fill=PROGRESS_TRACK_BG, outline="")
        fill_width = width * progress / 100
        if fill_width > 0:
            canvas.create_rectangle(
                0,
                0,
                fill_width,
                height,
                fill=progress_color(progress),
                outline="",
            )
        text_color = "#ffffff" if progress >= 55 else CARD_FG
        canvas.create_text(
            width / 2,
            height / 2,
            text=f"{progress}%",
            fill=text_color,
            font=self._metrics.progress_font,
        )

    def _label(self, parent: tk.Misc, **kwargs) -> tk.Label:
        defaults = {
            "bg": CARD_BG,
            "wraplength": self._metrics.card_label_wrap,
            "justify": tk.LEFT,
            "anchor": tk.W,
        }
        defaults.update(kwargs)
        return tk.Label(parent, **defaults)

    def _finalize_frame(self, frame: tk.Frame) -> None:
        metrics = self._metrics
        frame.update_idletasks()
        frame.config(
            width=max(metrics.card_min_width, frame.winfo_reqwidth()),
            height=max(metrics.card_min_height, frame.winfo_reqheight()),
        )
        frame.pack_propagate(False)

    def _create_progress_canvas(self, parent: tk.Frame, card: Card) -> tk.Canvas:
        canvas = tk.Canvas(
            parent,
            height=self._metrics.progress_bar_height,
            bg=PROGRESS_TRACK_BG,
            highlightthickness=0,
            bd=0,
        )
        self._progress_widgets[card.id] = canvas

        def redraw(_event: tk.Event | None = None) -> None:
            self.draw_progress(canvas, card.progress)

        canvas.bind("<Configure>", redraw)
        parent.after_idle(redraw)
        return canvas

    def _create_due_date_panel(self, frame: tk.Frame, card: Card) -> tuple[tk.Frame, tk.Label]:
        panel_bg, panel_fg = due_date_panel_style(card.due_date)
        due_panel = tk.Frame(
            frame,
            bg=panel_bg,
            bd=DUE_PANEL_BD,
            relief=tk.GROOVE,
            highlightthickness=0,
            padx=6,
            pady=3,
        )
        due_label = tk.Label(
            due_panel,
            text=format_due_date(card.due_date),
            bg=panel_bg,
            fg=panel_fg,
            font=self._metrics.due_font,
            anchor=tk.W,
            cursor="hand2",
        )
        due_label.pack(anchor=tk.W, fill=tk.X)
        return due_panel, due_label
