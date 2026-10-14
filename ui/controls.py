"""Graph-editing controls and algorithm result presentation."""

import math
import time
from typing import Dict, Optional, Tuple

from .constants import BLUE, BLUE_HOVER, BORDER_SOFT, ERROR, MUTED, SOFT_TEXT, WHITE

class ControlsMixin:
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
