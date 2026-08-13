"""カード UI の描画（FR-026 スケール / FR-028 テーマ対応）."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from petatto_kanban.card_ui import CardUiRefs
from petatto_kanban.display.ui_metrics import UiMetrics
from petatto_kanban.display.ui_theme import UiTheme, palette_for_theme
from petatto_kanban.due_date import due_date_panel_style, format_due_date
from petatto_kanban.models import Card
from petatto_kanban.progress import progress_color

if TYPE_CHECKING:
    from collections.abc import Callable

    from petatto_kanban.display.ui_theme import UiThemePalette

_DEFAULT_PALETTE = palette_for_theme(UiTheme.DEFAULT)
CARD_BG = _DEFAULT_PALETTE.card_bg
CARD_FG = _DEFAULT_PALETTE.card_fg
CARD_TITLE_FRAME_BD = 1
DUE_PANEL_BD = 1


class CardRenderer:
    """UiMetrics と UiThemePalette に基づきカードウィジェットを構築する."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        metrics: UiMetrics,
        palette: UiThemePalette,
        on_card_enter: Callable[[tk.Event], None],
        progress_widgets: dict[str, tk.Canvas],
    ) -> None:
        self._parent = parent
        self._metrics = metrics
        self._palette = palette
        self._on_card_enter = on_card_enter
        self._progress_widgets = progress_widgets

    @property
    def metrics(self) -> UiMetrics:
        return self._metrics

    @property
    def palette(self) -> UiThemePalette:
        return self._palette

    def render(self, card: Card) -> CardUiRefs:
        metrics = self._metrics
        palette = self._palette
        frame = tk.Frame(
            self._parent,
            bg=palette.card_bg,
            bd=metrics.card_frame_border,
            relief=tk.RIDGE,
            padx=metrics.card_frame_pad,
            pady=metrics.card_frame_pad,
            highlightthickness=0,
        )
        frame.place(x=card.x, y=card.y)

        title_frame = tk.Frame(
            frame,
            bg=palette.card_bg,
            bd=CARD_TITLE_FRAME_BD,
            relief=tk.GROOVE,
            highlightthickness=0,
            padx=metrics.card_title_frame_padx,
            pady=metrics.card_title_frame_pady,
        )
        title_frame.pack(anchor=tk.NW, fill=tk.X)

        title_label = self._label(
            title_frame,
            text=card.title,
            font=metrics.title_font,
            fg=palette.card_fg,
            cursor="xterm",
        )
        title_label.pack(anchor=tk.NW, fill=tk.X)

        due_panel, due_label = self._create_due_date_panel(frame, card)
        due_panel.pack(anchor=tk.NW, fill=tk.X, pady=(metrics.card_due_section_gap, 0))

        progress_canvas = self._create_progress_canvas(frame, card)
        progress_canvas.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            pady=(metrics.card_progress_section_gap, 0),
        )

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
        palette = self._palette
        bar_height = self._metrics.progress_bar_height
        canvas.delete("all")
        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), bar_height)
        canvas.create_rectangle(
            0, 0, width, height, fill=palette.progress_track_bg, outline=""
        )
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
        text_color = "#ffffff" if progress >= 55 else palette.card_fg
        canvas.create_text(
            width / 2,
            height / 2,
            text=f"{progress}%",
            fill=text_color,
            font=self._metrics.progress_font,
        )

    def _label(self, parent: tk.Misc, **kwargs) -> tk.Label:
        defaults = {
            "bg": self._palette.card_bg,
            "wraplength": self._metrics.card_label_wrap,
            "justify": tk.LEFT,
            "anchor": tk.W,
        }
        defaults.update(kwargs)
        return tk.Label(parent, **defaults)

    def _finalize_frame(self, frame: tk.Frame) -> None:
        metrics = self._metrics
        frame.update_idletasks()
        # 幅は card_min_width に固定。fill=X 子要素があると winfo_reqwidth が
        # 親キャンバス幅まで膨らみ、カードが不必要に横長になるため。
        frame.config(
            width=metrics.card_min_width,
            height=metrics.card_min_height,
        )
        frame.pack_propagate(False)

    def _create_progress_canvas(self, parent: tk.Frame, card: Card) -> tk.Canvas:
        palette = self._palette
        canvas = tk.Canvas(
            parent,
            height=self._metrics.progress_bar_height,
            bg=palette.progress_track_bg,
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
        metrics = self._metrics
        panel_bg, panel_fg = due_date_panel_style(card.due_date, palette=self._palette)
        due_panel = tk.Frame(
            frame,
            bg=panel_bg,
            bd=DUE_PANEL_BD,
            relief=tk.GROOVE,
            highlightthickness=0,
            padx=metrics.card_due_panel_padx,
            pady=metrics.card_due_panel_pady,
        )
        due_label = tk.Label(
            due_panel,
            text=format_due_date(card.due_date),
            bg=panel_bg,
            fg=panel_fg,
            font=self._metrics.due_font,
            anchor=tk.W,
            wraplength=metrics.card_label_wrap,
            justify=tk.LEFT,
            cursor="hand2",
        )
        due_label.pack(anchor=tk.W, fill=tk.X)
        return due_panel, due_label
