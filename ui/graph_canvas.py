"""Drawing of graph edges, labels, nodes, and active algorithm paths."""

import math
import time
import tkinter as tk
from typing import List, Optional, Tuple, TYPE_CHECKING, cast

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
    PATH_GREEN,
    START_OUTLINE,
    TARGET_OUTLINE,
    TRACE_EDGE,
    VISITED_FILL,
    VISITED_OUTLINE,
    WHITE,
)

if TYPE_CHECKING:
    from .app import DijkstraLab

class GraphCanvasMixin:
    def _on_endpoint_selected(self, selected_node: str) -> None:
        app = cast("DijkstraLab", self)
        if selected_node in app.graph.nodes:
            if app.start_node.get() != app.dynamic_algorithm.start:
                app.dynamic_graph = copy_graph(app.graph)
                app.dynamic_algorithm = DynamicDijkstra(
                    app.dynamic_graph, app.start_node.get()
                )
                dynamic_started = time.perf_counter()
                app.dynamic_algorithm.compute_shortest_paths()
                app.dynamic_time_ms = (time.perf_counter() - dynamic_started) * 1000
            app._calculate_classic()
            app.trace_index = 0
            app._refresh_trace_data()
            app._refresh_comparison()
            app._refresh_trace_view()

    def _draw_graph(self, event: Optional[tk.Event] = None) -> None:
        app = cast("DijkstraLab", self)
        if not hasattr(self, "graph_canvas"):
            return

        canvas = app.graph_canvas
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
            if node in app.graph.nodes
        }
        trace_step = app._current_trace_step()
        classic_path_edges = set(zip(app.classic_path, app.classic_path[1:]))
        dynamic_path = app.dynamic_algorithm.get_path(app.target_node.get())
        dynamic_path_edges = set(zip(dynamic_path, dynamic_path[1:]))
        active_node = trace_step.node if trace_step else None
        updated_nodes = set(trace_step.updated_nodes) if trace_step else set()
        trace_edges = {
            (active_node, node) for node in updated_nodes
        } if active_node else set()

        for source in sorted(app.graph.nodes):
            for dest, _ in sorted(app.graph.get_neighbors(source)):
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
                is_classic_edge = (source, dest) in classic_path_edges
                is_dynamic_edge = (source, dest) in dynamic_path_edges
                is_trace_edge = (source, dest) in trace_edges
                control = EDGE_CONTROL_POSITIONS.get((source, dest))
                has_reverse = app.graph.get_weight(dest, source) is not None
                edge_control = (
                    (
                        pad_x + control[0] * max(width - 2 * pad_x, 1),
                        pad_y + control[1] * max(height - 2 * pad_y, 1),
                    )
                    if control is not None
                    else None
                )
                edge_start = (start_x, start_y)
                edge_end = (end_x, end_y)
                app._draw_directed_edge(
                    canvas,
                    edge_start,
                    edge_end,
                    edge_control,
                    has_reverse,
                    TRACE_EDGE if is_trace_edge else EDGE_MUTED,
                    3 if is_trace_edge else 1.7,
                )
                shared_path_edge = is_classic_edge and is_dynamic_edge
                if is_classic_edge:
                    app._draw_directed_edge(
                        canvas,
                        edge_start,
                        edge_end,
                        edge_control,
                        has_reverse,
                        PATH_BLUE,
                        3,
                        -2.5 if shared_path_edge else 0,
                    )
                if is_dynamic_edge:
                    app._draw_directed_edge(
                        canvas,
                        edge_start,
                        edge_end,
                        edge_control,
                        has_reverse,
                        PATH_GREEN,
                        3,
                        2.5 if shared_path_edge else 0,
                    )

        for source in sorted(app.graph.nodes):
            for dest, weight in sorted(app.graph.get_neighbors(source)):
                if source not in positions or dest not in positions:
                    continue
                label_position = EDGE_LABEL_POSITIONS.get((source, dest))
                if label_position is None:
                    x1, y1 = positions[source]
                    x2, y2 = positions[dest]
                    label_x, label_y = (x1 + x2) / 2, (y1 + y2) / 2
                    if app.graph.get_weight(dest, source) is not None:
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
            elif node == app.start_node.get() == app.target_node.get():
                fill, outline = TRACE_EDGE, ORANGE
            elif node == app.start_node.get():
                fill, outline = NODE_START, START_OUTLINE
            elif node == app.target_node.get():
                fill, outline = NODE_TARGET, TARGET_OUTLINE
            else:
                fill, outline = WHITE, NODE_OUTLINE
            distance = app.classic_distances.get(node, float("inf"))
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

        app.graph_summary.configure(
            text=f"{app.graph.get_node_count()} sommets  ·  "
            f"{app.graph.get_edge_count()} arêtes  ·  "
            f"{app.start_node.get()} → {app.target_node.get()}"
        )

    @staticmethod
    def _draw_directed_edge(
        canvas: tk.Canvas,
        start: Tuple[float, float],
        end: Tuple[float, float],
        control: Optional[Tuple[float, float]],
        has_reverse: bool,
        color: str,
        width: float,
        offset: float = 0,
    ) -> None:
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = max((dx * dx + dy * dy) ** 0.5, 1)
        normal = (-dy / length * offset, dx / length * offset)
        shifted_start = (start[0] + normal[0], start[1] + normal[1])
        shifted_end = (end[0] + normal[0], end[1] + normal[1])

        if control is None and not has_reverse:
            coordinates = (*shifted_start, *shifted_end)
            smooth = False
            splinesteps = None
        else:
            if control is None:
                control = (
                    (start[0] + end[0]) / 2 - dy / length * 20,
                    (start[1] + end[1]) / 2 + dx / length * 20,
                )
            shifted_control = (control[0] + normal[0], control[1] + normal[1])
            curve_points = GraphCanvasMixin._curve_points(
                shifted_start, shifted_control, shifted_end
            )
            coordinates = tuple(
                coordinate for point in curve_points for coordinate in point
            )
            smooth = True
            splinesteps = 20

        options = {
            "fill": color,
            "width": width,
            "arrow": tk.LAST,
            "arrowshape": (10, 12, 5),
            "smooth": smooth,
        }
        if splinesteps is not None:
            options["splinesteps"] = splinesteps
        canvas.create_line(*coordinates, **options)

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
