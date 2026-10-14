"""Algorithm trace generation and playback controls."""

import heapq
from typing import List, Optional

from .models import TraceStep
from .constants import BLUE, MUTED

class TraceMixin:
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
