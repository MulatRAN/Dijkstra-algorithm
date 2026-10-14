"""CustomTkinter interface for the dynamic Dijkstra learning app."""

from __future__ import annotations

import tkinter as tk
import heapq
import math
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import customtkinter as ctk

from src.dijkstra import dijkstra, reconstruct_path
from src.dynamic_algo import DynamicDijkstra
from src.graph import DynamicGraph


@dataclass(frozen=True)
class TraceStep:
    """Presentation model for a single algorithm animation step."""

    node: Optional[str]
    distance: float
    visited: Tuple[str, ...]
    updated_nodes: Tuple[str, ...]
    explanation: str


BACKGROUND = "#F4F7FB"
CARD = "#FFFFFF"
INK = "#17243A"
MUTED = "#718096"
BLUE = "#3267E9"
BLUE_HOVER = "#2453C5"
PURPLE = "#7856D8"
ORANGE = "#D97706"
ERROR = "#B42318"
LINE = "#E2E8F0"
CANVAS = "#F8FAFD"
WHITE = "#FFFFFF"
CONTROL_BG = "#EDF1F7"
CONTROL_HOVER = "#DCE4EF"
CONTROL_HOVER_STRONG = "#CFD9E8"
PANEL_BG = "#F1F5F9"
SOFT_TEXT = "#64748B"
STRONG_MUTED = "#334155"
BADGE_BG = "#E8EEF8"
BADGE_TEXT = "#475569"
BORDER_SOFT = "#CBD5E1"
DISABLED_TEXT = "#94A3B8"
SELECTOR_BG = "#F0F4FA"
SELECTOR_BUTTON = "#E1E9F5"
SELECTOR_HOVER = "#D5E1F2"
NODE_START = "#D1D5DB"
NODE_TARGET = "#EDE9FE"
PATH_BLUE = "#2563EB"
NODE_ACTIVE = "#FDE68A"
DISTANCE_UPDATED = "#FEF3C7"
TRACE_EDGE = "#F59E0B"
EDGE_MUTED = "#65758B"
VISITED_FILL = "#E0E7FF"
VISITED_OUTLINE = "#818CF8"
START_OUTLINE = "#444444"
TARGET_OUTLINE = "#7C3AED"
NODE_OUTLINE = "#555555"
CANVAS_TEXT = "#202020"
NODE_TEXT = "#222222"
SPACE = 8
CARD_RADIUS = 14
CONTROL_RADIUS = 8
STATUS_RADIUS = 9
MARKER_RADIUS = 5
FONT_FAMILY = "Manrope"
CANVAS_FONT_FAMILY = "Segoe UI"
FONT_CAPTION = 10
FONT_BODY = 12
FONT_SECTION = 18
FONT_TITLE = 30
INITIAL_WINDOW_GEOMETRY = "1280x900"
WINDOW_MIN_SIZE = (420, 560)
WIDE_LAYOUT_MIN_WIDTH = 1040
COMPARISON_COLUMNS_MIN_WIDTH = 760
PLAYBACK_GRID_MAX_WIDTH = 1200
LEGEND_THREE_COLUMN_MIN_WIDTH = 900
CANVAS_WIDE_MIN_HEIGHT = 440
CANVAS_STACK_MIN_HEIGHT = 380
PAGE_PADDING = 30
CARD_PADDING = 18
NODE_WIDTH = 96
NODE_HEIGHT = 48
NODE_POSITIONS: Dict[str, Tuple[float, float]] = {
    "A": (0.13, 0.50),
    "B": (0.38, 0.18),
    "C": (0.38, 0.82),
    "D": (0.69, 0.19),
    "E": (0.87, 0.69),
}
DEMO_CONNECTIONS: Tuple[Tuple[str, str, float], ...] = (
    ("A", "B", 4.0),
    ("A", "C", 1.0),
    ("C", "B", 2.0),
    ("B", "D", 1.0),
    ("C", "D", 5.0),
    ("D", "E", 3.0),
    ("B", "E", 7.0),
)
EDGE_LABEL_POSITIONS: Dict[Tuple[str, str], Tuple[float, float]] = {
    ("A", "B"): (0.24, 0.31),
    ("A", "C"): (0.24, 0.70),
    ("C", "B"): (0.42, 0.50),
    ("B", "D"): (0.54, 0.13),
    ("C", "D"): (0.55, 0.48),
    ("D", "E"): (0.82, 0.40),
    ("B", "E"): (0.66, 0.39),
}
EDGE_CONTROL_POSITIONS: Dict[Tuple[str, str], Tuple[float, float]] = {
    ("B", "E"): (0.78, 0.25),
}


def build_demo_graph() -> DynamicGraph:
    """Build the directed graph used in the project's README example."""
    graph = DynamicGraph()
    for source, dest, weight in DEMO_CONNECTIONS:
        graph.add_edge(source, dest, weight)
    return graph


def copy_graph(graph: DynamicGraph) -> DynamicGraph:
    """Make an independent graph copy for the dynamic algorithm."""
    copied = DynamicGraph()
    for node in graph.nodes:
        copied.add_node(node)
    for source in graph.nodes:
        for dest, weight in graph.get_neighbors(source):
            copied.add_edge(source, dest, weight)
    return copied


class DijkstraLab(ctk.CTk):
    """Main desktop window for exploring the Dijkstra algorithms."""

    def __init__(self) -> None:
        super().__init__()
        self.graph = build_demo_graph()
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

    def _calculate_classic(self) -> None:
        started = time.perf_counter()
        self.classic_distances, self.classic_predecessors = dijkstra(
            self.graph, self.start_node.get()
        )
        self.classic_time_ms = (time.perf_counter() - started) * 1000
        self.classic_path = reconstruct_path(
            self.classic_predecessors,
            self.start_node.get(),
            self.target_node.get(),
        )
        self.classic_steps = self._trace_classic()

    def _trace_classic(self) -> List[TraceStep]:
        """Record Dijkstra's settled-node and relaxation steps for playback."""
        distances = {node: float("inf") for node in self.graph.nodes}
        distances[self.start_node.get()] = 0
        queue = [(0.0, self.start_node.get())]
        visited = set()
        steps = []

        while queue:
            distance, current = heapq.heappop(queue)
            if current in visited or distance > distances[current]:
                continue
            visited.add(current)
            updates = []
            for neighbor, weight in self.graph.get_neighbors(current):
                candidate = distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    heapq.heappush(queue, (candidate, neighbor))
                    updates.append(f"{neighbor}={candidate:g}")

            change_text = ", ".join(updates) if updates else "aucune distance modifiée"
            steps.append(
                TraceStep(
                    node=current,
                    distance=distance,
                    visited=tuple(sorted(visited)),
                    updated_nodes=tuple(update.split("=")[0] for update in updates),
                    explanation=f"Distance définitive de {current} : {distance:g}. "
                    f"Relâchement : {change_text}.",
                )
            )

        return steps

    def _refresh_trace_data(self) -> None:
        if self.trace_algorithm.get() == "Dijkstra dynamique":
            visited = []
            self.trace_steps = []
            for step in self.dynamic_algorithm.last_trace:
                visited.append(step.node)
                if step.invalidated:
                    action = f"distance de {step.node} invalidée"
                else:
                    action = f"distance de {step.node} fixée à {step.new_distance:g}"
                updated = ", ".join(step.updated_nodes) or "aucune"
                self.trace_steps.append(
                    TraceStep(
                        node=step.node,
                        distance=step.new_distance,
                        visited=tuple(dict.fromkeys(visited)),
                        updated_nodes=step.updated_nodes,
                        explanation=f"{action}. Valeur rhs : {step.rhs_value:g}. "
                        f"Sommets affectés : {updated}.",
                    )
                )
            if not self.trace_steps:
                self.trace_steps = [
                    TraceStep(
                        node=None,
                        distance=0,
                        visited=(),
                        updated_nodes=(),
                        explanation="Aucun sommet incohérent à traiter : "
                        "la modification ne change pas les plus courts chemins.",
                    )
                ]
        else:
            self.trace_steps = list(self.classic_steps)
        self.trace_index = min(self.trace_index, len(self.trace_steps) - 1)

    def _on_trace_algorithm_changed(self, selected: str) -> None:
        self.trace_algorithm.set(selected)
        self._stop_trace_playback()
        self.trace_index = 0
        self._refresh_trace_data()
        self._refresh_trace_view()
        self._draw_graph()

    def _current_trace_step(self) -> Optional[TraceStep]:
        if not self.trace_steps:
            return None
        return self.trace_steps[self.trace_index]

    def _refresh_trace_view(self) -> None:
        if not hasattr(self, "trace_counter"):
            return
        step = self._current_trace_step()
        self.trace_counter.configure(
            text=f"Étape {self.trace_index + 1} sur {len(self.trace_steps)}"
            if self.trace_steps
            else "Étape 0 sur 0"
        )
        self.trace_explanation.configure(
            text=step.explanation if step else "Aucune étape disponible."
        )
        self.restart_button.configure(
            state="disabled" if self.trace_index == 0 else "normal"
        )
        self.previous_button.configure(
            state="disabled" if self.trace_index == 0 else "normal"
        )
        self.next_button.configure(
            state=(
                "disabled"
                if not self.trace_steps or self.trace_index >= len(self.trace_steps) - 1
                else "normal"
            )
        )
        if hasattr(self, "graph_play_status"):
            step_number = self.trace_index + 1 if self.trace_steps else 0
            active_node = f" · sommet {step.node}" if step and step.node else ""
            prefix = "Lecture active" if self.trace_after_id is not None else "Étape"
            self.graph_play_status.configure(
                text=(
                    f"{prefix} {step_number} sur {len(self.trace_steps)}"
                    f"{active_node}."
                ),
                text_color=BLUE if self.trace_after_id is not None else MUTED,
            )
        self._draw_graph()

    def _stop_trace_playback(self) -> None:
        if self.trace_after_id is not None:
            self.after_cancel(self.trace_after_id)
            self.trace_after_id = None
        if hasattr(self, "play_button"):
            self.play_button.configure(text="▶ Lire")
        if hasattr(self, "graph_play_status"):
            self._refresh_trace_view()

    def _restart_trace(self) -> None:
        self._stop_trace_playback()
        self.trace_index = 0
        self._refresh_trace_view()

    def _previous_trace_step(self) -> None:
        self._stop_trace_playback()
        self.trace_index = max(0, self.trace_index - 1)
        self._refresh_trace_view()

    def _next_trace_step(self) -> None:
        self._stop_trace_playback()
        self.trace_index = min(len(self.trace_steps) - 1, self.trace_index + 1)
        self._refresh_trace_view()

    def _toggle_trace_playback(self) -> None:
        if self.trace_after_id is not None:
            self._stop_trace_playback()
            return
        if self.trace_index >= len(self.trace_steps) - 1:
            self.trace_index = 0
            self._refresh_trace_view()
        self.play_button.configure(text="⏸ Pause")
        self.trace_after_id = self.after(700, self._advance_trace_playback)
        self._refresh_trace_view()

    def _advance_trace_playback(self) -> None:
        self.trace_after_id = None
        if self.trace_index >= len(self.trace_steps) - 1:
            self._stop_trace_playback()
            return
        self.trace_index += 1
        self.trace_after_id = self.after(700, self._advance_trace_playback)
        self._refresh_trace_view()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.header = header
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            header,
            text="Dijkstra Lab",
            text_color=INK,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_TITLE, weight="bold"),
        )
        self.header_title.grid(row=0, column=0, sticky="w")
        self.header_subtitle = ctk.CTkLabel(
            header,
            text="Visualisez la différence entre recalcul complet et mise à jour dynamique.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_BODY + 2),
        )
        self.header_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.header_badge = ctk.CTkLabel(
            header,
            text="MODE DÉMONSTRATION",
            text_color=BADGE_TEXT,
            fg_color=BADGE_BG,
            corner_radius=CONTROL_RADIUS,
            padx=11,
            pady=6,
            font=ctk.CTkFont(size=FONT_CAPTION, weight="bold"),
        )
        self.header_badge.grid(row=0, column=1, rowspan=2, sticky="e")
        self.header.grid_columnconfigure(1, weight=0)

    def _build_workspace(self) -> None:
        workspace = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.workspace = workspace
        workspace.grid(row=1, column=0, sticky="nsew", padx=30)
        workspace.grid_columnconfigure(0, weight=64, uniform="dashboard")
        workspace.grid_columnconfigure(1, weight=36, uniform="dashboard")
        workspace.grid_rowconfigure(0, weight=1)

        graph_card = self._card(workspace)
        self.graph_card = graph_card
        graph_card.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        graph_card.grid_columnconfigure(0, weight=1)
        graph_card.grid_rowconfigure(4, weight=1, minsize=420)
        self._section_heading(
            graph_card, "01  ·  GRAPHE ORIENTÉ ET PONDÉRÉ", "Graphe actif"
        )
        self.graph_subtitle = ctk.CTkLabel(
            graph_card,
            text="Le chemin sélectionné et les étapes de calcul sont mis en évidence.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_BODY),
            anchor="w",
        )
        self.graph_subtitle.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 12))
        self.graph_canvas = tk.Canvas(
            graph_card,
            bg=CANVAS,
            highlightthickness=0,
            relief="flat",
        )
        self.graph_canvas.grid(row=4, column=0, sticky="nsew", padx=18, pady=(0, 10))
        self.graph_canvas.bind("<Configure>", self._draw_graph)

        legend = ctk.CTkFrame(graph_card, fg_color="transparent")
        self.legend_frame = legend
        legend.grid(row=5, column=0, sticky="ew", padx=22, pady=(2, 0))
        self.legend_items = [
            self._legend_item(legend, "Départ", NODE_START, 0),
            self._legend_item(legend, "Arrivée", NODE_TARGET, 1, outlined=True),
            self._legend_item(legend, "Chemin optimal", PATH_BLUE, 2),
            self._legend_item(legend, "Sommet actif", NODE_ACTIVE, 3, outlined=True),
            self._legend_item(
                legend, "Distance mise à jour", DISTANCE_UPDATED, 4, outlined=True
            ),
        ]

        self.graph_summary = ctk.CTkLabel(
            graph_card,
            text="",
            text_color=MUTED,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        )
        self.graph_summary.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=CARD_PADDING,
            pady=(SPACE, SPACE * 2),
        )
        self.graph_play_status = ctk.CTkLabel(
            graph_card,
            text="Étape prête à explorer.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_CAPTION),
            anchor="w",
        )
        self.graph_play_status.grid(
            row=7, column=0, sticky="ew", padx=22, pady=(0, 14)
        )

        controls = self._card(workspace)
        self.controls_card = controls
        controls.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        controls.grid_columnconfigure((0, 1), weight=1, uniform="edit-controls")
        self._section_heading(
            controls, "PARCOURS", "Configurez l’expérience", columnspan=2
        )

        self.controls_subtitle = ctk.CTkLabel(
            controls,
            text="Choisissez un trajet, modifiez une arête et comparez.",
            text_color=MUTED,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
            wraplength=280,
        )
        self.controls_subtitle.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8)
        )
        self.endpoint_selectors = ctk.CTkFrame(controls, fg_color="transparent")
        self.endpoint_selectors.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10)
        )
        self.endpoint_selectors.grid_columnconfigure(
            (0, 1), weight=1, uniform="endpoints"
        )
        self._selector(self.endpoint_selectors, "Départ", self.start_node, 0, SOFT_TEXT)
        self._selector(self.endpoint_selectors, "Arrivée", self.target_node, 1, PURPLE)
        ctk.CTkLabel(
            controls,
            text="2. Modifier une arête",
            text_color=INK,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 6))
        ctk.CTkLabel(
            controls,
            text="Action",
            text_color=MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(row=5, column=0, sticky="w", padx=(18, 8), pady=(0, 4))
        ctk.CTkOptionMenu(
            controls,
            variable=self.change_type,
            values=["Modifier le poids", "Supprimer une arête", "Ajouter une arête"],
            command=self._on_change_type,
            fg_color=CONTROL_BG,
            button_color=CONTROL_HOVER,
            button_hover_color=CONTROL_HOVER,
            text_color=INK,
            dropdown_text_color=INK,
            height=34,
        ).grid(row=5, column=1, sticky="ew", padx=(0, 18), pady=(0, 4))

        self.edge_label = ctk.CTkLabel(
            controls,
            text="Arête",
            text_color=MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.edge_label.grid(row=6, column=0, sticky="w", padx=(18, 8), pady=(0, 4))
        self.edge_menu = ctk.CTkOptionMenu(
            controls,
            variable=self.edge_selection,
            values=[],
            fg_color=CONTROL_BG,
            button_color=CONTROL_HOVER,
            button_hover_color=CONTROL_HOVER,
            text_color=INK,
            dropdown_text_color=INK,
        )
        self.edge_menu.grid(row=6, column=1, sticky="ew", padx=(0, 18), pady=(0, 4))

        self.weight_label = ctk.CTkLabel(
            controls,
            text="Nouveau poids",
            text_color=MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.weight_label.grid(row=7, column=0, sticky="w", padx=(18, 8), pady=(0, 5))
        self.weight_entry = ctk.CTkEntry(
            controls,
            textvariable=self.new_weight,
            placeholder_text="Ex. 5.5",
            height=36,
        )
        self.weight_entry.grid(row=7, column=1, sticky="ew", padx=(0, 18), pady=(0, 5))

        self.apply_button = ctk.CTkButton(
            controls,
            text="Appliquer",
            command=self._apply_change,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            text_color=WHITE,
            height=42,
            corner_radius=STATUS_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY + 1, weight="bold"),
        )
        self.apply_button.grid(
            row=8, column=0, columnspan=2, sticky="ew", padx=18, pady=(2, 7)
        )
        self.change_status = ctk.CTkLabel(
            controls,
            text="Prêt · les résultats suivent chaque action.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_CAPTION + 1),
            justify="left",
            anchor="w",
            wraplength=280,
        )
        self.change_status.grid(
            row=9, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 5)
        )
        self._refresh_edge_options()

    def _refresh_edge_options(self) -> None:
        add_mode = self.change_type.get() == "Ajouter une arête"
        options: Dict[str, Tuple[str, str]] = {}
        if add_mode:
            for source in self.nodes:
                for dest in self.nodes:
                    if source != dest and self.graph.get_weight(source, dest) is None:
                        options[f"{source} → {dest}"] = (source, dest)
            self.edge_label.configure(text="Nouvelle arête (sens de parcours)")
        else:
            for source in sorted(self.graph.nodes):
                for dest, weight in sorted(self.graph.get_neighbors(source)):
                    options[f"{source} → {dest}   ·   {weight:g}"] = (source, dest)
            self.edge_label.configure(text="Arête concernée")

        self.edge_options = options
        values = list(options)
        self.edge_menu.configure(values=values, state="normal" if values else "disabled")
        if values:
            selected = values[0]
            self.edge_selection.set(selected)
            self.edge_menu.set(selected)
        else:
            self.edge_selection.set("")
            self.edge_menu.set("Aucune arête disponible")

        remove_mode = self.change_type.get() == "Supprimer une arête"
        self.weight_label.grid() if not remove_mode else self.weight_label.grid_remove()
        self.weight_entry.grid() if not remove_mode else self.weight_entry.grid_remove()
        self.weight_label.configure(
            text="Poids de la nouvelle arête" if add_mode else "Nouveau poids"
        )
        self.apply_button.configure(
            state="normal" if values else "disabled",
            fg_color=BLUE if values else BORDER_SOFT,
            hover_color=BLUE_HOVER if values else BORDER_SOFT,
            text_color=WHITE if values else SOFT_TEXT,
        )
        self.apply_button.configure(
            text="Ajouter l'arête" if add_mode else
            "Supprimer l'arête" if remove_mode else "Appliquer"
        )
        self.weight_entry.configure(
            state="disabled" if remove_mode else "normal",
            placeholder_text="Non requis" if remove_mode else "Ex. 5.5",
        )
        if remove_mode:
            self.new_weight.set("")
        elif not self.new_weight.get():
            self.new_weight.set("5")

    def _on_change_type(self, selected: str) -> None:
        self.change_type.set(selected)
        self._refresh_edge_options()
        self._set_control_status("Sélectionnez l'arête à modifier.")

    def _set_control_status(self, message: str, error: bool = False) -> None:
        self.change_status.configure(
            text=message,
            text_color=ERROR if error else MUTED,
        )

    def _apply_change(self) -> None:
        selected_edge = self.edge_selection.get()
        edge = self.edge_options.get(selected_edge)
        if edge is None:
            self._set_control_status("Sélectionnez une arête valide.", error=True)
            return

        source, dest = edge
        operation = self.change_type.get()
        new_weight: Optional[float] = None
        if operation != "Supprimer une arête":
            try:
                new_weight = float(self.new_weight.get())
            except ValueError:
                self._set_control_status("Entrez un poids numérique valide.", error=True)
                return
            if not math.isfinite(new_weight) or new_weight < 0:
                self._set_control_status(
                    "Le poids doit être un nombre fini positif ou nul.",
                    error=True,
                )
                return

        if operation == "Supprimer une arête":
            self.graph.remove_edge(source, dest)
        else:
            self.graph.add_edge(source, dest, new_weight)

        dynamic_started = time.perf_counter()
        self.dynamic_algorithm.handle_edge_weight_change(source, dest, new_weight)
        self.dynamic_time_ms = (time.perf_counter() - dynamic_started) * 1000
        self._calculate_classic()
        self.change_count += 1
        self.trace_index = 0
        self._refresh_trace_data()
        self._refresh_edge_options()
        self._refresh_comparison()
        self._refresh_trace_view()
        self._set_control_status(
            f"Modification appliquée : {source} → {dest}."
        )

    def _refresh_comparison(self) -> None:
        target = self.target_node.get()
        classic_distance = self.classic_distances.get(target, float("inf"))
        dynamic_distance = self.dynamic_algorithm.distances.get(target, float("inf"))

        if self.change_count:
            self.classic_result_labels["status"].configure(
                text="Modification · recalcul complet"
            )
            self.dynamic_result_labels["status"].configure(
                text="Modification · mise à jour incrémentale"
            )
        else:
            self.classic_result_labels["status"].configure(text="État initial")
            self.dynamic_result_labels["status"].configure(text="État initial")

        self.classic_result_labels["path"].configure(
            text="Chemin : " + (" → ".join(self.classic_path) if self.classic_path else "inaccessible")
        )
        dynamic_path = self.dynamic_algorithm.get_path(target)
        self.dynamic_result_labels["path"].configure(
            text="Chemin : " + (" → ".join(dynamic_path) if dynamic_path else "inaccessible")
        )
        self.classic_result_labels["distance"].configure(
            text=f"Coût total : {classic_distance:g}"
            if math.isfinite(classic_distance)
            else "Coût total : inaccessible"
        )
        self.dynamic_result_labels["distance"].configure(
            text=f"Coût total : {dynamic_distance:g}"
            if math.isfinite(dynamic_distance)
            else "Coût total : inaccessible"
        )
        self.classic_result_labels["time"].configure(
            text=f"Mesure sur ce graphe · {self.classic_time_ms:.4f} ms"
        )
        self.dynamic_result_labels["time"].configure(
            text=f"Mesure sur ce graphe · {self.dynamic_time_ms:.4f} ms"
        )
        classic_updates = sum(
            len(step.updated_nodes) for step in self.classic_steps
        )
        dynamic_trace = self.dynamic_algorithm.last_trace
        dynamic_updates = sum(len(step.updated_nodes) for step in dynamic_trace)
        self.classic_result_labels["processed"].configure(
            text=f"Sommets finalisés · {len(self.classic_steps)}"
        )
        self.classic_result_labels["updates"].configure(
            text=f"Relâchements réussis · {classic_updates}"
        )
        self.dynamic_result_labels["processed"].configure(
            text=f"Sommets réparés · {len(dynamic_trace)}"
        )
        self.dynamic_result_labels["updates"].configure(
            text=f"Valeurs rhs modifiées · {dynamic_updates}"
        )
        self.graph_summary.configure(
            text=f"{self.graph.get_node_count()} sommets  ·  "
            f"{self.graph.get_edge_count()} arêtes  ·  "
            f"{self.start_node.get()} → {target}"
        )

    def _build_comparison(self) -> None:
        comparison = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        self.comparison_frame = comparison
        comparison.grid(row=11, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 10))
        comparison.grid_columnconfigure((0, 1), weight=1)
        self.comparison_heading = ctk.CTkLabel(
            comparison,
            text="3. Comparer les résultats",
            text_color=INK,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.comparison_heading.grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 3)
        )
        self.comparison_explainer = ctk.CTkLabel(
            comparison,
            text=(
                "Temps et travail : finalisations/relâchements côté classique, "
                "réparations/valeurs rhs côté dynamique."
            ),
            text_color=MUTED,
            font=ctk.CTkFont(size=10),
            justify="left",
            anchor="w",
            wraplength=350,
        )
        self.comparison_explainer.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 7)
        )
        self.algorithm_cards: List[ctk.CTkFrame] = []
        self._algorithm_path_labels: List[ctk.CTkLabel] = []

        self._algorithm_card(
            comparison,
            column=0,
            title="Dijkstra classique",
            accent=BLUE,
            result_key="classic",
        )
        self._algorithm_card(
            comparison,
            column=1,
            title="Dijkstra dynamique",
            accent=PURPLE,
            result_key="dynamic",
        )
        playback = self._card(self.content_frame)
        self.playback_card = playback
        playback.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 16))
        playback.grid_columnconfigure(0, weight=0)
        playback.grid_columnconfigure(1, weight=1)
        playback.grid_columnconfigure(2, weight=0)
        self.playback_title = ctk.CTkLabel(
            playback,
            text="4. Explorer le calcul",
            text_color=INK,
            font=ctk.CTkFont(size=FONT_SECTION - 2, weight="bold"),
        )
        self.playback_title.grid(row=0, column=0, sticky="w", padx=18, pady=(12, 1))
        self.playback_subtitle = ctk.CTkLabel(
            playback,
            text="Suivez les sommets traités et les distances mises à jour.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_BODY),
        )
        self.playback_subtitle.grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 8)
        )
        self.trace_menu = ctk.CTkOptionMenu(
            playback,
            variable=self.trace_algorithm,
            values=["Dijkstra classique", "Dijkstra dynamique"],
            command=self._on_trace_algorithm_changed,
            width=205,
            height=32,
            fg_color=CONTROL_BG,
            button_color=CONTROL_HOVER,
            button_hover_color=CONTROL_HOVER_STRONG,
            text_color=INK,
            dropdown_text_color=INK,
        )
        self.trace_menu.grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=10)

        controls = ctk.CTkFrame(playback, fg_color="transparent")
        self.playback_controls = controls
        controls.grid(
            row=0, column=2, rowspan=2, sticky="ew", padx=12, pady=(8, 8)
        )
        self.restart_button = ctk.CTkButton(
            controls,
            text="⏮ Début",
            width=100,
            height=36,
            command=self._restart_trace,
            fg_color=CONTROL_BG,
            hover_color=CONTROL_HOVER,
            text_color=INK,
            text_color_disabled=DISABLED_TEXT,
        )
        self.previous_button = ctk.CTkButton(
            controls,
            text="◀ Précédent",
            width=128,
            height=36,
            command=self._previous_trace_step,
            fg_color=CONTROL_BG,
            hover_color=CONTROL_HOVER,
            text_color=INK,
            text_color_disabled=DISABLED_TEXT,
        )
        self.play_button = ctk.CTkButton(
            controls,
            text="▶ Lire",
            width=102,
            height=36,
            command=self._toggle_trace_playback,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            text_color=WHITE,
        )
        self.next_button = ctk.CTkButton(
            controls,
            text="Suivant ▶",
            width=112,
            height=36,
            command=self._next_trace_step,
            fg_color=CONTROL_BG,
            hover_color=CONTROL_HOVER,
            text_color=INK,
            text_color_disabled=DISABLED_TEXT,
        )
        self.playback_button_widgets = [
            self.restart_button,
            self.previous_button,
            self.play_button,
            self.next_button,
        ]
        self.trace_counter = ctk.CTkLabel(
            controls,
            text="Étape 0 sur 0",
            text_color=MUTED,
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.trace_counter.grid(row=0, column=4, sticky="e", padx=8)
        self.trace_explanation = ctk.CTkLabel(
            playback,
            text="Choisissez un algorithme puis avancez étape par étape.",
            text_color=STRONG_MUTED,
            fg_color=PANEL_BG,
            corner_radius=STATUS_RADIUS,
            wraplength=1000,
            justify="left",
            anchor="w",
            padx=12,
            pady=10,
            font=ctk.CTkFont(size=11),
        )
        self.trace_explanation.grid(
            row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(2, 12)
        )
        self.playback_mode = ""

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

    @staticmethod
    def _card(parent: ctk.CTkBaseClass) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=LINE,
        )

    def _section_heading(
        self,
        parent: ctk.CTkFrame,
        eyebrow: str,
        title: str,
        columnspan: int = 1,
    ) -> None:
        ctk.CTkLabel(
            parent,
            text=eyebrow,
            text_color=MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(
            row=0, column=0, columnspan=columnspan, sticky="ew", padx=22, pady=(18, 3)
        )
        ctk.CTkLabel(
            parent,
            text=title,
            text_color=INK,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=1, column=0, columnspan=columnspan, sticky="ew", padx=22, pady=(0, 12)
        )

    def _selector(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.StringVar,
        column: int,
        accent: str,
    ) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="ew", padx=(0, 10) if column == 0 else 0)
        ctk.CTkLabel(
            frame,
            text=f"●  {label}",
            text_color=accent,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 5))
        menu = ctk.CTkOptionMenu(
            frame,
            variable=variable,
            values=self.nodes,
            fg_color=SELECTOR_BG,
            button_color=SELECTOR_BUTTON,
            button_hover_color=SELECTOR_HOVER,
            text_color=INK,
            dropdown_text_color=INK,
            command=self._on_endpoint_selected,
            height=34,
        )
        menu.pack(fill="x")

    def _legend_item(
        self,
        parent: ctk.CTkFrame,
        label: str,
        color: str,
        column: int,
        outlined: bool = False,
    ) -> ctk.CTkFrame:
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.grid(row=0, column=column, sticky="w", padx=(0, 8), pady=2)
        ctk.CTkFrame(
            item,
            width=10,
            height=10,
            corner_radius=MARKER_RADIUS,
            fg_color=color,
            border_width=1 if outlined else 0,
            border_color=BORDER_SOFT,
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            item,
            text=label,
            text_color=MUTED,
            font=ctk.CTkFont(size=10),
        ).pack(side="left")
        return item

    def _layout_legend(self, columns: int) -> None:
        for column in range(5):
            self.legend_frame.grid_columnconfigure(column, weight=0)
        for column in range(columns):
            self.legend_frame.grid_columnconfigure(column, weight=1)
        for index, item in enumerate(self.legend_items):
            item.grid_configure(row=index // columns, column=index % columns, sticky="w")

    def _algorithm_card(
        self,
        parent: ctk.CTkFrame,
        column: int,
        title: str,
        accent: str,
        result_key: str,
    ) -> None:
        card = self._card(parent)
        self.algorithm_cards.append(card)
        card.grid(row=2, column=column, sticky="nsew", padx=(0, 7) if column == 0 else (7, 0))
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card,
            text=title,
            text_color=INK,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 1))
        status = ctk.CTkLabel(
            card,
            text="Prêt · calcul initial",
            text_color=accent,
            fg_color=SELECTOR_BG,
            corner_radius=8,
            padx=9,
            pady=4,
            font=ctk.CTkFont(size=10, weight="bold"),
        )
        status.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 5))
        path_label = ctk.CTkLabel(
            card,
            text="Chemin : —",
            text_color=INK,
            wraplength=380,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._algorithm_path_labels.append(path_label)
        path_label.grid(row=2, column=0, sticky="ew", padx=18, pady=(3, 5))
        distance_label = ctk.CTkLabel(
            card,
            text="Coût total : —",
            text_color=INK,
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        distance_label.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 3))
        time_label = ctk.CTkLabel(
            card,
            text="Mesure sur ce graphe : —",
            text_color=MUTED,
            anchor="w",
            font=ctk.CTkFont(size=11),
        )
        time_label.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 15))
        processed_label = ctk.CTkLabel(
            card,
            text="Sommets traités · —",
            text_color=INK,
            anchor="w",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        processed_label.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 2))
        updates_label = ctk.CTkLabel(
            card,
            text="Mises à jour · —",
            text_color=MUTED,
            anchor="w",
            font=ctk.CTkFont(size=10),
        )
        updates_label.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 12))
        labels = {
            "status": status,
            "path": path_label,
            "distance": distance_label,
            "time": time_label,
            "processed": processed_label,
            "updates": updates_label,
        }
        if result_key == "classic":
            self.classic_result_labels = labels
        else:
            self.dynamic_result_labels = labels

    def _on_endpoint_selected(self, selected_node: str) -> None:
        if selected_node in self.graph.nodes:
            if self.start_node.get() != self.dynamic_algorithm.start:
                self.dynamic_graph = copy_graph(self.graph)
                self.dynamic_algorithm = DynamicDijkstra(
                    self.dynamic_graph, self.start_node.get()
                )
                dynamic_started = time.perf_counter()
                self.dynamic_algorithm.compute_shortest_paths()
                self.dynamic_time_ms = (time.perf_counter() - dynamic_started) * 1000
            self._calculate_classic()
            self.trace_index = 0
            self._refresh_trace_data()
            self._refresh_comparison()
            self._refresh_trace_view()

    def _draw_graph(self, event: Optional[tk.Event] = None) -> None:
        if not hasattr(self, "graph_canvas"):
            return

        canvas = self.graph_canvas
        canvas.delete("all")
        width = max(event.width if event else canvas.winfo_width(), 1)
        height = max(event.height if event else canvas.winfo_height(), 1)
        node_width = min(NODE_WIDTH, max(64, width * 0.14))
        node_height = min(NODE_HEIGHT, max(36, width * 0.07))
        pad_x = node_width / 2 + 16
        pad_y = node_height / 2 + 16
        positions = {
            node: (
                pad_x + x_ratio * max(width - 2 * pad_x, 1),
                pad_y + y_ratio * max(height - 2 * pad_y, 1),
            )
            for node, (x_ratio, y_ratio) in NODE_POSITIONS.items()
            if node in self.graph.nodes
        }
        trace_step = self._current_trace_step()
        path = (
            self.classic_path
            if self.trace_algorithm.get() == "Dijkstra classique"
            else self.dynamic_algorithm.get_path(self.target_node.get())
        )
        path_edges = set(zip(path, path[1:]))
        active_node = trace_step.node if trace_step else None
        updated_nodes = set(trace_step.updated_nodes) if trace_step else set()
        trace_edges = {
            (active_node, node) for node in updated_nodes
        } if active_node else set()

        for source in sorted(self.graph.nodes):
            for dest, _ in sorted(self.graph.get_neighbors(source)):
                if source not in positions or dest not in positions:
                    continue
                x1, y1 = positions[source]
                x2, y2 = positions[dest]
                dx, dy = x2 - x1, y2 - y1
                length = max((dx * dx + dy * dy) ** 0.5, 1)
                ux, uy = dx / length, dy / length
                node_radius = 1 / (
                    (ux / (node_width / 2)) ** 2
                    + (uy / (node_height / 2)) ** 2
                ) ** 0.5
                start_x = x1 + ux * node_radius
                start_y = y1 + uy * node_radius
                end_x = x2 - ux * (node_radius + 5)
                end_y = y2 - uy * (node_radius + 5)
                is_path_edge = (source, dest) in path_edges
                is_trace_edge = (source, dest) in trace_edges
                color = (
                    TRACE_EDGE if is_trace_edge else
                    PATH_BLUE if is_path_edge else EDGE_MUTED
                )
                line_width = 3 if is_path_edge or is_trace_edge else 1.7
                control = EDGE_CONTROL_POSITIONS.get((source, dest))
                has_reverse = self.graph.get_weight(dest, source) is not None
                if control is None:
                    if has_reverse:
                        normal_x, normal_y = -uy, ux
                        control_x = (start_x + end_x) / 2 + normal_x * 20
                        control_y = (start_y + end_y) / 2 + normal_y * 20
                    else:
                        control_x = control_y = 0
                    if has_reverse:
                        points = self._curve_points(
                            (start_x, start_y),
                            (control_x, control_y),
                            (end_x, end_y),
                        )
                        canvas.create_line(
                            *[coordinate for point in points for coordinate in point],
                            fill=color,
                            width=line_width,
                            arrow=tk.LAST,
                            arrowshape=(10, 12, 5),
                            smooth=True,
                        )
                    else:
                        canvas.create_line(
                            start_x,
                            start_y,
                            end_x,
                            end_y,
                            fill=color,
                            width=line_width,
                            arrow=tk.LAST,
                            arrowshape=(10, 12, 5),
                        )
                else:
                    control_x = pad_x + control[0] * max(width - 2 * pad_x, 1)
                    control_y = pad_y + control[1] * max(height - 2 * pad_y, 1)
                    points = self._curve_points(
                        (start_x, start_y),
                        (control_x, control_y),
                        (end_x, end_y),
                    )
                    canvas.create_line(
                        *[coordinate for point in points for coordinate in point],
                        fill=color,
                        width=line_width,
                        arrow=tk.LAST,
                        arrowshape=(10, 12, 5),
                        smooth=True,
                        splinesteps=20,
                    )

        for source in sorted(self.graph.nodes):
            for dest, weight in sorted(self.graph.get_neighbors(source)):
                if source not in positions or dest not in positions:
                    continue
                label_position = EDGE_LABEL_POSITIONS.get((source, dest))
                if label_position is None:
                    x1, y1 = positions[source]
                    x2, y2 = positions[dest]
                    label_x, label_y = (x1 + x2) / 2, (y1 + y2) / 2
                    if self.graph.get_weight(dest, source) is not None:
                        dx, dy = x2 - x1, y2 - y1
                        length = max((dx * dx + dy * dy) ** 0.5, 1)
                        label_x += -dy / length * 24
                        label_y += dx / length * 24
                else:
                    label_x = pad_x + label_position[0] * max(width - 2 * pad_x, 1)
                    label_y = pad_y + label_position[1] * max(height - 2 * pad_y, 1)
                label = f"{weight:g}"
                label_width = max(15, len(label) * 4 + 5)
                canvas.create_rectangle(
                    label_x - label_width,
                    label_y - 10,
                    label_x + label_width,
                    label_y + 10,
                    fill=CANVAS,
                    outline=CANVAS,
                )
                canvas.create_text(
                    label_x,
                    label_y,
                    text=label,
                    fill=CANVAS_TEXT,
                    font=(CANVAS_FONT_FAMILY, FONT_CAPTION, "bold"),
                )

        for node, (x, y) in positions.items():
            if node == active_node:
                fill, outline = NODE_ACTIVE, ORANGE
            elif node in updated_nodes:
                fill, outline = DISTANCE_UPDATED, TRACE_EDGE
            elif trace_step and node in trace_step.visited:
                fill, outline = VISITED_FILL, VISITED_OUTLINE
            elif node == self.start_node.get() == self.target_node.get():
                fill, outline = TRACE_EDGE, ORANGE
            elif node == self.start_node.get():
                fill, outline = NODE_START, START_OUTLINE
            elif node == self.target_node.get():
                fill, outline = NODE_TARGET, TARGET_OUTLINE
            else:
                fill, outline = WHITE, NODE_OUTLINE
            distance = self.classic_distances.get(node, float("inf"))
            distance_text = f"{distance:g}" if math.isfinite(distance) else "∞"
            canvas.create_oval(
                x - node_width / 2,
                y - node_height / 2,
                x + node_width / 2,
                y + node_height / 2,
                fill=fill,
                outline=outline,
                width=1.4,
            )
            canvas.create_text(
                x,
                y,
                text=f"{node} ({distance_text})",
                fill=NODE_TEXT,
                font=(
                    CANVAS_FONT_FAMILY,
                    max(8, min(FONT_CAPTION, int(width / 60))),
                ),
            )

        self.graph_summary.configure(
            text=f"{self.graph.get_node_count()} sommets  ·  "
            f"{self.graph.get_edge_count()} arêtes  ·  "
            f"{self.start_node.get()} → {self.target_node.get()}"
        )

    @staticmethod
    def _curve_points(
        start: Tuple[float, float],
        control: Tuple[float, float],
        end: Tuple[float, float],
    ) -> List[Tuple[float, float]]:
        points = []
        for step in range(17):
            t = step / 16
            inverse = 1 - t
            points.append(
                (
                    inverse * inverse * start[0]
                    + 2 * inverse * t * control[0]
                    + t * t * end[0],
                    inverse * inverse * start[1]
                    + 2 * inverse * t * control[1]
                    + t * t * end[1],
                )
            )
        return points


if __name__ == "__main__":
    app = DijkstraLab()
    app.mainloop()
