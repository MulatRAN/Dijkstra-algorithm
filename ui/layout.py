"""Responsive layout and reusable presentation helpers."""

import tkinter as tk
from typing import List

import customtkinter as ctk

from .constants import (
    CANVAS_STACK_MIN_HEIGHT,
    CANVAS_WIDE_MIN_HEIGHT,
    COMPARISON_COLUMNS_MIN_WIDTH,
    FONT_TITLE,
    LEGEND_THREE_COLUMN_MIN_WIDTH,
    PAGE_PADDING,
    PLAYBACK_GRID_MAX_WIDTH,
    WIDE_LAYOUT_MIN_WIDTH,
)

class LayoutMixin:
    def _on_window_configure(self, event: tk.Event) -> None:
        if event.widget is not self:
            return
        if self._resize_after_id is not None:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(80, self._apply_responsive_layout)

    def _apply_responsive_layout(self) -> None:
        self._resize_after_id = None
        width = self.content_frame.winfo_width()
        workspace_mode = "columns" if width >= WIDE_LAYOUT_MIN_WIDTH else "stack"
        playback_mode = "row" if width >= PLAYBACK_GRID_MAX_WIDTH else "grid"
        margin = (
            PAGE_PADDING
            if width >= WIDE_LAYOUT_MIN_WIDTH
            else 22
            if width >= COMPARISON_COLUMNS_MIN_WIDTH
            else 14
        )

        self.header.grid_configure(padx=margin, pady=(12, 8))
        self.workspace.grid_configure(padx=margin)
        self.playback_card.grid_configure(padx=margin, pady=(10, 16))
        self.header_title.configure(
            font=ctk.CTkFont(
                size=FONT_TITLE if width >= COMPARISON_COLUMNS_MIN_WIDTH else FONT_TITLE - 5,
                weight="bold",
            )
        )
        self.header_subtitle.configure(
            wraplength=max(260, width - margin * 2 - 32)
        )
        if width < 640:
            self.header_badge.grid_configure(row=2, column=0, rowspan=1, sticky="w")
        else:
            self.header_badge.grid_configure(row=0, column=1, rowspan=2, sticky="e")

        if workspace_mode != self.workspace_mode:
            self.workspace_mode = workspace_mode
            if workspace_mode == "columns":
                self.workspace.grid_columnconfigure(0, weight=64, uniform="dashboard")
                self.workspace.grid_columnconfigure(1, weight=36, uniform="dashboard")
                self.workspace.grid_rowconfigure(0, weight=1)
                self.workspace.grid_rowconfigure(1, weight=0)
                self.graph_card.grid_configure(row=0, column=0, padx=(0, 10), pady=0)
                self.controls_card.grid_configure(
                    row=0, column=1, padx=(10, 0), pady=0
                )
                self.graph_card.grid_rowconfigure(
                    4, weight=1, minsize=CANVAS_WIDE_MIN_HEIGHT
                )
            else:
                self.workspace.grid_columnconfigure(0, weight=1, uniform="")
                self.workspace.grid_columnconfigure(1, weight=0, uniform="")
                self.workspace.grid_rowconfigure(0, weight=0)
                self.workspace.grid_rowconfigure(1, weight=0)
                self.graph_card.grid_configure(row=0, column=0, padx=0, pady=(0, 12))
                self.controls_card.grid_configure(row=1, column=0, padx=0, pady=0)
                self.graph_card.grid_rowconfigure(
                    4, weight=0, minsize=CANVAS_STACK_MIN_HEIGHT
                )

        if playback_mode != self.playback_mode:
            self.playback_mode = playback_mode
            self._layout_playback_controls(playback_mode)
        self._layout_legend(
            3
            if width >= LEGEND_THREE_COLUMN_MIN_WIDTH
            else 2
            if width >= PLAYBACK_GRID_MAX_WIDTH
            else 1
        )

        self.after_idle(self._update_responsive_text)

    def _update_responsive_text(self) -> None:
        if not self.winfo_exists():
            return
        self.controls_subtitle.configure(
            wraplength=max(220, self.controls_card.winfo_width() - 44)
        )
        self.endpoint_selectors.configure(
            width=max(240, self.controls_card.winfo_width() - 36)
        )
        self.trace_explanation.configure(
            wraplength=max(220, self.playback_card.winfo_width() - 48)
        )
        self.comparison_explainer.configure(
            wraplength=max(220, self.comparison_frame.winfo_width() - 32)
        )
        for card, labels in zip(self.algorithm_cards, self._algorithm_path_labels):
            labels.configure(wraplength=max(220, card.winfo_width() - 44))
        self.header_subtitle.configure(
            wraplength=max(240, self.header.winfo_width() - 130)
        )
        self.graph_subtitle.configure(
            wraplength=max(260, self.graph_card.winfo_width() - 52)
        )

    def _layout_playback_controls(self, mode: str) -> None:
        for button in self.playback_button_widgets:
            button.grid_forget()
        self.trace_counter.grid_forget()
        for column in range(5):
            self.playback_controls.grid_columnconfigure(column, weight=0)

        if mode == "row":
            self.playback_title.grid_configure(row=0, column=0)
            self.playback_subtitle.grid_configure(row=1, column=0)
            self.trace_menu.grid_configure(
                row=0, column=1, columnspan=1, rowspan=2, sticky="e"
            )
            self.playback_controls.grid_configure(
                row=0, column=2, columnspan=1, rowspan=2, sticky="ew"
            )
            self.trace_explanation.grid_configure(row=2, column=0, columnspan=3)
            widths = (100, 128, 102, 112)
            for column, (button, width) in enumerate(
                zip(self.playback_button_widgets, widths)
            ):
                button.configure(width=width)
                button.grid(row=0, column=column, padx=3, sticky="ew")
            self.playback_controls.grid_columnconfigure(4, weight=1)
            self.trace_counter.grid(row=0, column=4, sticky="e", padx=(8, 4))
        else:
            self.playback_title.grid_configure(row=0, column=0)
            self.playback_subtitle.grid_configure(row=1, column=0)
            self.trace_menu.grid_configure(
                row=2, column=0, columnspan=3, rowspan=1, sticky="ew", padx=18
            )
            self.playback_controls.grid_configure(
                row=3, column=0, columnspan=3, rowspan=1, sticky="ew"
            )
            self.trace_explanation.grid_configure(
                row=4, column=0, columnspan=3, sticky="ew"
            )
            self.playback_controls.grid_columnconfigure(0, weight=1)
            self.playback_controls.grid_columnconfigure(1, weight=1)
            self.restart_button.configure(width=140)
            self.previous_button.configure(width=140)
            self.play_button.configure(width=140)
            self.next_button.configure(width=140)
            self.restart_button.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
            self.previous_button.grid(row=0, column=1, padx=3, pady=3, sticky="ew")
            self.play_button.grid(row=1, column=0, padx=3, pady=3, sticky="ew")
            self.next_button.grid(row=1, column=1, padx=3, pady=3, sticky="ew")
            self.trace_counter.grid(
                row=2, column=0, columnspan=2, sticky="w", padx=4, pady=(2, 4)
            )

    def _layout_legend(self, columns: int) -> None:
        for column in range(5):
            self.legend_frame.grid_columnconfigure(column, weight=0)
        for column in range(columns):
            self.legend_frame.grid_columnconfigure(column, weight=1)
        for index, item in enumerate(self.legend_items):
            item.grid_configure(row=index // columns, column=index % columns, sticky="w")
