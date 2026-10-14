"""Responsive layout and reusable presentation helpers."""

import tkinter as tk
from typing import TYPE_CHECKING, cast

import customtkinter as ctk

from .constants import (
    CANVAS_STACK_MIN_HEIGHT,
    CANVAS_WIDE_MIN_HEIGHT,
    COMPARISON_COLUMNS_MIN_WIDTH,
    FONT_TITLE,
    LEGEND_THREE_COLUMN_MIN_WIDTH,
    PAGE_PADDING,
    WIDE_LAYOUT_MIN_WIDTH,
)

if TYPE_CHECKING:
    from .app import DijkstraLab

class LayoutMixin:
    def _on_window_configure(self, event: tk.Event) -> None:
        app = cast("DijkstraLab", self)
        if event.widget is not self:
            return
        if app._resize_after_id is not None:
            app.after_cancel(app._resize_after_id)
        app._resize_after_id = app.after(80, app._apply_responsive_layout)

    def _apply_responsive_layout(self) -> None:
        app = cast("DijkstraLab", self)
        app._resize_after_id = None
        width = app.content_frame.winfo_width()
        workspace_mode = "columns" if width >= WIDE_LAYOUT_MIN_WIDTH else "stack"
        margin = (
            PAGE_PADDING
            if width >= WIDE_LAYOUT_MIN_WIDTH
            else 22
            if width >= COMPARISON_COLUMNS_MIN_WIDTH
            else 14
        )

        app.header.grid_configure(padx=margin, pady=(12, 8))
        app.workspace.grid_configure(padx=margin)
        app.header_title.configure(
            font=ctk.CTkFont(
                size=FONT_TITLE if width >= COMPARISON_COLUMNS_MIN_WIDTH else FONT_TITLE - 5,
                weight="bold",
            )
        )
        app.header_subtitle.configure(
            wraplength=max(260, width - margin * 2 - 32)
        )
        if width < 640:
            app.header_badge.grid_configure(row=2, column=0, rowspan=1, sticky="w")
        else:
            app.header_badge.grid_configure(row=0, column=1, rowspan=2, sticky="e")

        if workspace_mode != app.workspace_mode:
            app.workspace_mode = workspace_mode
            if workspace_mode == "columns":
                app.workspace.grid_columnconfigure(0, weight=64, uniform="dashboard")
                app.workspace.grid_columnconfigure(1, weight=36, uniform="dashboard")
                app.workspace.grid_rowconfigure(0, weight=1)
                app.workspace.grid_rowconfigure(1, weight=0)
                app.graph_card.grid_configure(row=0, column=0, padx=(0, 10), pady=0)
                app.controls_card.grid_configure(
                    row=0, column=1, padx=(10, 0), pady=0
                )
                app.graph_card.grid_rowconfigure(
                    4, weight=1, minsize=CANVAS_WIDE_MIN_HEIGHT
                )
            else:
                app.workspace.grid_columnconfigure(0, weight=1, uniform="")
                app.workspace.grid_columnconfigure(1, weight=0, uniform="")
                app.workspace.grid_rowconfigure(0, weight=0)
                app.workspace.grid_rowconfigure(1, weight=0)
                app.graph_card.grid_configure(row=0, column=0, padx=0, pady=(0, 12))
                app.controls_card.grid_configure(row=1, column=0, padx=0, pady=0)
                app.graph_card.grid_rowconfigure(
                    4, weight=0, minsize=CANVAS_STACK_MIN_HEIGHT
                )

        app._layout_legend(
            3
            if width >= LEGEND_THREE_COLUMN_MIN_WIDTH
            else 2
            if width >= COMPARISON_COLUMNS_MIN_WIDTH
            else 1
        )

        app.after_idle(app._update_responsive_text)

    def _update_responsive_text(self) -> None:
        app = cast("DijkstraLab", self)
        if not app.winfo_exists():
            return
        app.controls_subtitle.configure(
            wraplength=max(220, app.controls_card.winfo_width() - 44)
        )
        app.endpoint_selectors.configure(
            width=max(240, app.controls_card.winfo_width() - 36)
        )
        app.comparison_explainer.configure(
            wraplength=max(220, app.comparison_frame.winfo_width() - 32)
        )
        for card, labels in zip(app.algorithm_cards, app._algorithm_path_labels):
            labels.configure(wraplength=max(220, card.winfo_width() - 44))
        app.header_subtitle.configure(
            wraplength=max(240, app.header.winfo_width() - 130)
        )
        app.graph_subtitle.configure(
            wraplength=max(260, app.graph_card.winfo_width() - 52)
        )

    def _layout_legend(self, columns: int) -> None:
        app = cast("DijkstraLab", self)
        for column in range(len(app.legend_items)):
            app.legend_frame.grid_columnconfigure(column, weight=0)
        for column in range(columns):
            app.legend_frame.grid_columnconfigure(column, weight=1)
        for index, item in enumerate(app.legend_items):
            item.grid_configure(row=index // columns, column=index % columns, sticky="w")
