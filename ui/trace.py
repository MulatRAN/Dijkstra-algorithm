"""Algorithm trace generation and playback controls."""

import heapq
from typing import List, Optional, TYPE_CHECKING, cast

from .models import TraceStep
from .constants import BLUE, MUTED

if TYPE_CHECKING:
    from .app import DijkstraLab

class TraceMixin:
    def _trace_classic(self) -> List[TraceStep]:
        """Record Dijkstra's settled-node and relaxation steps for playback."""
        app = cast("DijkstraLab", self)
        distances = {node: float("inf") for node in app.classic_graph.nodes}
        distances[app.start_node.get()] = 0
        queue = [(0.0, app.start_node.get())]
        visited = set()
        steps = []

        while queue:
            distance, current = heapq.heappop(queue)
            if current in visited or distance > distances[current]:
                continue
            visited.add(current)
            updates = []
            for neighbor, weight in app.classic_graph.get_neighbors(current):
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
        app = cast("DijkstraLab", self)
        if app.trace_algorithm.get() == "Dijkstra dynamique":
            visited = []
            app.trace_steps = []
            for step in app.dynamic_algorithm.last_trace:
                visited.append(step.node)
                if step.invalidated:
                    action = f"distance de {step.node} invalidée"
                else:
                    action = f"distance de {step.node} fixée à {step.new_distance:g}"
                updated = ", ".join(step.updated_nodes) or "aucune"
                app.trace_steps.append(
                    TraceStep(
                        node=step.node,
                        distance=step.new_distance,
                        visited=tuple(dict.fromkeys(visited)),
                        updated_nodes=step.updated_nodes,
                        explanation=f"{action}. Valeur rhs : {step.rhs_value:g}. "
                        f"Sommets affectés : {updated}.",
                    )
                )
            if not app.trace_steps:
                app.trace_steps = [
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
            app.trace_steps = list(app.classic_steps)
        app.trace_index = min(app.trace_index, len(app.trace_steps) - 1)

    def _on_trace_algorithm_changed(self, selected: str) -> None:
        app = cast("DijkstraLab", self)
        app.trace_algorithm.set(selected)
        app._stop_trace_playback()
        app.trace_index = 0
        app._refresh_trace_data()
        app._refresh_trace_view()
        app._draw_graph()

    def _current_trace_step(self) -> Optional[TraceStep]:
        app = cast("DijkstraLab", self)
        if not app.trace_steps:
            return None
        return app.trace_steps[app.trace_index]

    def _refresh_trace_view(self) -> None:
        app = cast("DijkstraLab", self)
        if not hasattr(self, "trace_counter"):
            return
        step = app._current_trace_step()
        app.trace_counter.configure(
            text=f"Étape {app.trace_index + 1} sur {len(app.trace_steps)}"
            if app.trace_steps
            else "Étape 0 sur 0"
        )
        app.trace_explanation.configure(
            text=step.explanation if step else "Aucune étape disponible."
        )
        app.restart_button.configure(
            state="disabled" if app.trace_index == 0 else "normal"
        )
        app.previous_button.configure(
            state="disabled" if app.trace_index == 0 else "normal"
        )
        app.next_button.configure(
            state=(
                "disabled"
                if not app.trace_steps or app.trace_index >= len(app.trace_steps) - 1
                else "normal"
            )
        )
        if hasattr(self, "graph_play_status"):
            step_number = app.trace_index + 1 if app.trace_steps else 0
            active_node = f" · sommet {step.node}" if step and step.node else ""
            prefix = "Lecture active" if app.trace_after_id is not None else "Étape"
            app.graph_play_status.configure(
                text=(
                    f"{prefix} {step_number} sur {len(app.trace_steps)}"
                    f"{active_node}."
                ),
                text_color=BLUE if app.trace_after_id is not None else MUTED,
            )
        app._draw_graph()

    def _stop_trace_playback(self) -> None:
        app = cast("DijkstraLab", self)
        if app.trace_after_id is not None:
            app.after_cancel(app.trace_after_id)
            app.trace_after_id = None
        if hasattr(self, "play_button"):
            app.play_button.configure(text="▶ Lire")
        if hasattr(self, "graph_play_status"):
            app._refresh_trace_view()

    def _restart_trace(self) -> None:
        app = cast("DijkstraLab", self)
        app._stop_trace_playback()
        app.trace_index = 0
        app._refresh_trace_view()

    def _previous_trace_step(self) -> None:
        app = cast("DijkstraLab", self)
        app._stop_trace_playback()
        app.trace_index = max(0, app.trace_index - 1)
        app._refresh_trace_view()

    def _next_trace_step(self) -> None:
        app = cast("DijkstraLab", self)
        app._stop_trace_playback()
        app.trace_index = min(len(app.trace_steps) - 1, app.trace_index + 1)
        app._refresh_trace_view()

    def _toggle_trace_playback(self) -> None:
        app = cast("DijkstraLab", self)
        if app.trace_after_id is not None:
            app._stop_trace_playback()
            return
        if app.trace_index >= len(app.trace_steps) - 1:
            app.trace_index = 0
            app._refresh_trace_view()
        app.play_button.configure(text="⏸ Pause")
        app.trace_after_id = app.after(700, app._advance_trace_playback)
        app._refresh_trace_view()

    def _advance_trace_playback(self) -> None:
        app = cast("DijkstraLab", self)
        app.trace_after_id = None
        if app.trace_index >= len(app.trace_steps) - 1:
            app._stop_trace_playback()
            return
        app.trace_index += 1
        app.trace_after_id = app.after(700, app._advance_trace_playback)
        app._refresh_trace_view()
