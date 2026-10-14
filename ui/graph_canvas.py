"""Drawing of graph edges, labels, nodes, and active algorithm paths."""

import math
import time
import tkinter as tk
from typing import List, Optional, Tuple

import customtkinter as ctk

from src.dynamic_algo import DynamicDijkstra

from .graph_data import copy_graph
from .constants import (
    CANVAS,
    CANVAS_FONT_FAMILY,
    CANVAS_TEXT,
    DISTANCE_UPDATED,
    EDGE_CONTROL_POSITIONS,
    EDGE_LABEL_POSITIONS,
    EDGE_MUTED,
    FONT_CAPTION,
    NODE_ACTIVE,
    NODE_HEIGHT,
    NODE_OUTLINE,
    NODE_POSITIONS,
    NODE_START,
    NODE_TARGET,
    NODE_TEXT,
    NODE_WIDTH,
    ORANGE,
    PATH_BLUE,
    START_OUTLINE,
    TARGET_OUTLINE,
    TRACE_EDGE,
    VISITED_FILL,
    VISITED_OUTLINE,
    WHITE,
)

class GraphCanvasMixin:
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
