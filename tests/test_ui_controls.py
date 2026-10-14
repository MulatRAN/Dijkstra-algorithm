"""Tests for graph-editing and result-presentation helpers."""
from types import SimpleNamespace
from typing import cast

from src.graph import DynamicGraph
from ui.controls import ControlsMixin, _current_path_cost


def test_current_path_cost_uses_latest_edge_weights():
    graph = DynamicGraph()
    graph.add_edge("A", "B", 2.0)
    graph.add_edge("B", "C", 3.0)
    path = ["A", "B", "C"]

    graph.update_weight("A", "B", 7.0)

    assert _current_path_cost(graph, path) == 10.0


def test_current_path_cost_is_unavailable_when_an_edge_was_removed():
    graph = DynamicGraph()
    graph.add_edge("A", "B", 2.0)
    graph.add_edge("B", "C", 3.0)
    graph.remove_edge("B", "C")

    assert _current_path_cost(graph, ["A", "B", "C"]) is None


def test_recalculate_classic_replaces_snapshot_without_changing_dynamic_graph():
    graph = DynamicGraph()
    graph.add_edge("A", "B", 5.0)
    graph.update_weight("A", "B", 2.0)
    dynamic_graph = DynamicGraph()
    dynamic_graph.add_edge("A", "B", 2.0)
    refreshed = []
    state = SimpleNamespace(
        graph=graph,
        dynamic_graph=dynamic_graph,
        classic_graph=DynamicGraph(),
        classic_snapshot_outdated=True,
        _calculate_classic=lambda: refreshed.append("calculated"),
        _refresh_comparison=lambda: refreshed.append("comparison"),
        _draw_graph=lambda: refreshed.append("draw_graph"),
        _set_control_status=lambda message: refreshed.append(message),
    )

    ControlsMixin._recalculate_classic(cast(ControlsMixin, state))

    assert state.classic_graph.get_weight("A", "B") == 2.0
    assert state.classic_graph is not graph
    assert state.classic_snapshot_outdated is False
    assert dynamic_graph.get_weight("A", "B") == 2.0
    assert refreshed == [
        "calculated",
        "comparison",
        "draw_graph",
        "Dijkstra classique recalculé sur le graphe actuel.",
    ]
