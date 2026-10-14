"""Tests for graph-editing and result-presentation helpers."""

from src.graph import DynamicGraph
from ui.controls import _current_path_cost


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
