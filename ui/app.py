"""Application window and orchestration for the Dijkstra Lab."""

from __future__ import annotations

import time
import tkinter as tk
from typing import Dict, List, Optional, Tuple

import customtkinter as ctk

from src.dijkstra import dijkstra, reconstruct_path
from src.dynamic_algo import DynamicDijkstra

from .constants import (
    BACKGROUND,
    BORDER_SOFT,
    DISABLED_TEXT,
    INITIAL_WINDOW_GEOMETRY,
    WINDOW_MIN_SIZE,
)
from .graph_data import build_demo_graph, copy_graph
from .controls import ControlsMixin
from .graph_canvas import GraphCanvasMixin
from .layout import LayoutMixin
from .models import TraceStep
from .panels import PanelsMixin
from .trace import TraceMixin

class DijkstraLab(
    TraceMixin,
    ControlsMixin,
    LayoutMixin,
    PanelsMixin,
    GraphCanvasMixin,
    ctk.CTk,
):
    header: ctk.CTkBaseClass
    header_title: ctk.CTkBaseClass
    header_subtitle: ctk.CTkBaseClass
    header_badge: ctk.CTkBaseClass
    workspace: ctk.CTkBaseClass
    graph_card: ctk.CTkBaseClass
    graph_subtitle: ctk.CTkBaseClass
    graph_canvas: tk.Canvas
    legend_frame: ctk.CTkBaseClass
    legend_items: List[ctk.CTkBaseClass]
    graph_summary: ctk.CTkBaseClass
    graph_play_status: ctk.CTkBaseClass
    controls_card: ctk.CTkBaseClass
    controls_subtitle: ctk.CTkBaseClass
    endpoint_selectors: ctk.CTkBaseClass
    edge_label: ctk.CTkBaseClass
    edge_menu: ctk.CTkOptionMenu
    weight_label: ctk.CTkBaseClass
    weight_entry: ctk.CTkBaseClass
    apply_button: ctk.CTkBaseClass
    change_status: ctk.CTkBaseClass
    comparison_frame: ctk.CTkBaseClass
    comparison_heading: ctk.CTkBaseClass
    comparison_explainer: ctk.CTkBaseClass
    algorithm_cards: List[ctk.CTkFrame]
    _algorithm_path_labels: List[ctk.CTkLabel]
    classic_result_labels: Dict[str, ctk.CTkLabel]
    dynamic_result_labels: Dict[str, ctk.CTkLabel]
    playback_card: ctk.CTkBaseClass
    playback_title: ctk.CTkBaseClass
    playback_subtitle: ctk.CTkBaseClass
    trace_menu: ctk.CTkBaseClass
    playback_controls: ctk.CTkBaseClass
    restart_button: ctk.CTkButton
    previous_button: ctk.CTkButton
    play_button: ctk.CTkButton
    next_button: ctk.CTkButton
    playback_button_widgets: List[ctk.CTkButton]
    trace_counter: ctk.CTkBaseClass
    trace_explanation: ctk.CTkBaseClass

    def __init__(self) -> None:
        super().__init__()
        self.graph = build_demo_graph()
        self.classic_graph = copy_graph(self.graph)
        self.nodes = sorted(self.graph.nodes)
        self.start_node = ctk.StringVar(value=self.nodes[0])
        self.target_node = ctk.StringVar(value=self.nodes[-1])
        self.change_type = ctk.StringVar(value="Modifier le poids")
        self.edge_selection = ctk.StringVar()
        self.new_weight = ctk.StringVar(value="5")
        self.edge_options: Dict[str, Tuple[str, str]] = {}
        self.classic_distances: Dict[str, float] = {}
        self.classic_predecessors: Dict[str, Optional[str]] = {}
        self.classic_path: List[str] = []
        self.classic_time_ms = 0.0
        self.dynamic_time_ms = 0.0
        self.dynamic_graph = copy_graph(self.graph)
        self.dynamic_algorithm = DynamicDijkstra(self.dynamic_graph, self.start_node.get())
        self.change_count = 0
        dynamic_started = time.perf_counter()
        self.dynamic_algorithm.compute_shortest_paths()
        self.dynamic_time_ms = (time.perf_counter() - dynamic_started) * 1000
        self._calculate_classic()
        self.trace_algorithm = ctk.StringVar(value="Dijkstra classique")
        self.trace_steps: List[TraceStep] = []
        self.trace_index = 0
        self.trace_after_id: Optional[str] = None
        self._refresh_trace_data()
        self.title("Dijkstra Lab | Algorithmes de plus court chemin")
        self.geometry(INITIAL_WINDOW_GEOMETRY)
        self.minsize(*WINDOW_MIN_SIZE)
        self.configure(fg_color=BACKGROUND)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BORDER_SOFT,
            scrollbar_button_hover_color=DISABLED_TEXT,
        )
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self._resize_after_id: Optional[str] = None
        self.workspace_mode = ""
        self.comparison_mode = ""
        self.playback_mode = ""
        self._build_header()
        self._build_workspace()
        self._build_comparison()
        self.bind("<Configure>", self._on_window_configure)
        self.after_idle(self._apply_responsive_layout)
        self._draw_graph()
        self._refresh_comparison()
        self._refresh_trace_view()

    def _calculate_classic(self) -> None:
        started = time.perf_counter()
        self.classic_distances, self.classic_predecessors = dijkstra(
            self.classic_graph, self.start_node.get()
        )
        self.classic_time_ms = (time.perf_counter() - started) * 1000
        self.classic_path = reconstruct_path(
            self.classic_predecessors,
            self.start_node.get(),
            self.target_node.get(),
        )
        self.classic_steps = self._trace_classic()

def main() -> None:
    """Launch the desktop application."""
    app = DijkstraLab()
    app.mainloop()
