"""Graph-editing controls and algorithm result presentation."""

import math
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, cast

from src.graph import DynamicGraph
from .graph_data import copy_graph
from .constants import BLUE, BLUE_HOVER, BORDER_SOFT, ERROR, MUTED, SOFT_TEXT, WHITE

if TYPE_CHECKING:
    from .app import DijkstraLab


def _current_path_cost(graph: DynamicGraph, path: List[str]) -> Optional[float]:
    if not path:
        return None

    total = 0.0
    for source, dest in zip(path, path[1:]):
        weight = graph.get_weight(source, dest)
        if weight is None:
            return None
        total += weight
    return total


class ControlsMixin:
    def _refresh_edge_options(self) -> None:
        app = cast("DijkstraLab", self)
        add_mode = app.change_type.get() == "Ajouter une arête"
        options: Dict[str, Tuple[str, str]] = {}
        if add_mode:
            for source in app.nodes:
                for dest in app.nodes:
                    if source != dest and app.graph.get_weight(source, dest) is None:
                        options[f"{source} → {dest}"] = (source, dest)
            app.edge_label.configure(text="Nouvelle arête (sens de parcours)")
        else:
            for source in sorted(app.graph.nodes):
                for dest, weight in sorted(app.graph.get_neighbors(source)):
                    options[f"{source} → {dest}   ·   {weight:g}"] = (source, dest)
            app.edge_label.configure(text="Arête concernée")

        app.edge_options = options
        values = list(options)
        app.edge_menu.configure(values=values, state="normal" if values else "disabled")
        if values:
            selected = values[0]
            app.edge_selection.set(selected)
            app.edge_menu.set(selected)
        else:
            app.edge_selection.set("")
            app.edge_menu.set("Aucune arête disponible")

        remove_mode = app.change_type.get() == "Supprimer une arête"
        app.weight_label.grid() if not remove_mode else app.weight_label.grid_remove()
        app.weight_entry.grid() if not remove_mode else app.weight_entry.grid_remove()
        app.weight_label.configure(
            text="Poids de la nouvelle arête" if add_mode else "Nouveau poids"
        )
        app.apply_button.configure(
            state="normal" if values else "disabled",
            fg_color=BLUE if values else BORDER_SOFT,
            hover_color=BLUE_HOVER if values else BORDER_SOFT,
            text_color=WHITE if values else SOFT_TEXT,
        )
        app.apply_button.configure(
            text="Ajouter l'arête" if add_mode else
            "Supprimer l'arête" if remove_mode else "Appliquer"
        )
        app.weight_entry.configure(
            state="disabled" if remove_mode else "normal",
            placeholder_text="Non requis" if remove_mode else "Ex. 5.5",
        )
        if remove_mode:
            app.new_weight.set("")
        elif not app.new_weight.get():
            app.new_weight.set("5")

    def _on_change_type(self, selected: str) -> None:
        app = cast("DijkstraLab", self)
        app.change_type.set(selected)
        app._refresh_edge_options()
        app._set_control_status("Sélectionnez l'arête à modifier.")

    def _set_control_status(self, message: str, error: bool = False) -> None:
        app = cast("DijkstraLab", self)
        app.change_status.configure(
            text=message,
            text_color=ERROR if error else MUTED,
        )

    def _apply_change(self) -> None:
        app = cast("DijkstraLab", self)
        selected_edge = app.edge_selection.get()
        edge = app.edge_options.get(selected_edge)
        if edge is None:
            app._set_control_status("Sélectionnez une arête valide.", error=True)
            return

        source, dest = edge
        operation = app.change_type.get()
        new_weight: Optional[float] = None
        if operation != "Supprimer une arête":
            try:
                new_weight = float(app.new_weight.get())
            except ValueError:
                app._set_control_status("Entrez un poids numérique valide.", error=True)
                return
            if not math.isfinite(new_weight) or new_weight < 0:
                app._set_control_status(
                    "Le poids doit être un nombre fini positif ou nul.",
                    error=True,
                )
                return

        if operation == "Supprimer une arête":
            app.graph.remove_edge(source, dest)
        else:
            assert new_weight is not None
            app.graph.add_edge(source, dest, new_weight)

        dynamic_started = time.perf_counter()
        app.dynamic_algorithm.handle_edge_weight_change(source, dest, new_weight)
        app.dynamic_time_ms = (time.perf_counter() - dynamic_started) * 1000
        app.change_count += 1
        app.classic_snapshot_outdated = True
        app.trace_index = 0
        app._refresh_trace_data()
        app._refresh_edge_options()
        app._refresh_comparison()
        app._refresh_trace_view()
        app._set_control_status(
            f"Modification appliquée : {source} → {dest}."
        )

    def _recalculate_classic(self) -> None:
        app = cast("DijkstraLab", self)
        app.classic_graph = copy_graph(app.graph)
        app._calculate_classic()
        app.classic_snapshot_outdated = False
        app.trace_index = 0
        app._refresh_trace_data()
        app._refresh_comparison()
        app._refresh_trace_view()
        app._set_control_status(
            "Dijkstra classique recalculé sur le graphe actuel."
        )

    def _refresh_comparison(self) -> None:
        app = cast("DijkstraLab", self)
        target = app.target_node.get()
        classic_distance = app.classic_distances.get(target, float("inf"))
        dynamic_distance = app.dynamic_algorithm.distances.get(target, float("inf"))
        classic_current_cost = _current_path_cost(app.graph, app.classic_path)

        if app.change_count:
            app.classic_result_labels["status"].configure(
                text=(
                    "Modification · graphe initial conservé"
                    if app.classic_snapshot_outdated
                    else "Recalculé · graphe actuel"
                )
            )
            app.dynamic_result_labels["status"].configure(
                text="Modification · mise à jour incrémentale"
            )
        else:
            app.classic_result_labels["status"].configure(text="État initial")
            app.dynamic_result_labels["status"].configure(text="État initial")

        app.classic_result_labels["path"].configure(
            text="Chemin : " + (" → ".join(app.classic_path) if app.classic_path else "inaccessible")
        )
        dynamic_path = app.dynamic_algorithm.get_path(target)
        app.dynamic_result_labels["path"].configure(
            text="Chemin : " + (" → ".join(dynamic_path) if dynamic_path else "inaccessible")
        )
        app.classic_result_labels["distance"].configure(
            text=(
                f"Coût réel actuel du chemin : {classic_current_cost:g}"
                if app.change_count and classic_current_cost is not None
                else "Coût réel actuel : chemin interrompu"
                if app.change_count and app.classic_path
                else "Coût réel actuel : inaccessible"
                if app.change_count
                else f"Coût total : {classic_distance:g}"
                if math.isfinite(classic_distance)
                else "Coût total : inaccessible"
            )
        )
        app.dynamic_result_labels["distance"].configure(
            text=f"Coût total : {dynamic_distance:g}"
            if math.isfinite(dynamic_distance)
            else "Coût total : inaccessible"
        )
        app.classic_result_labels["time"].configure(
            text=(
                f"Mesure sur le graphe initial · {app.classic_time_ms:.4f} ms"
                if app.classic_snapshot_outdated
                else f"Mesure sur ce graphe · {app.classic_time_ms:.4f} ms"
            )
        )
        app.dynamic_result_labels["time"].configure(
            text=f"Mesure sur ce graphe · {app.dynamic_time_ms:.4f} ms"
        )
        classic_updates = sum(
            len(step.updated_nodes) for step in app.classic_steps
        )
        dynamic_trace = app.dynamic_algorithm.last_trace
        dynamic_updates = sum(len(step.updated_nodes) for step in dynamic_trace)
        app.classic_result_labels["processed"].configure(
            text=f"Sommets finalisés · {len(app.classic_steps)}"
        )
        app.classic_result_labels["updates"].configure(
            text=f"Relâchements réussis · {classic_updates}"
        )
        app.dynamic_result_labels["processed"].configure(
            text=f"Sommets réparés · {len(dynamic_trace)}"
        )
        app.dynamic_result_labels["updates"].configure(
            text=f"Valeurs rhs modifiées · {dynamic_updates}"
        )
        app.graph_summary.configure(
            text=f"{app.graph.get_node_count()} sommets  ·  "
            f"{app.graph.get_edge_count()} arêtes  ·  "
            f"{app.start_node.get()} → {target}"
        )
