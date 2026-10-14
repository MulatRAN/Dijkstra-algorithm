"""Tests for algorithm trace generation."""
from types import SimpleNamespace

from src.graph import DynamicGraph
from ui.trace import TraceMixin


def test_classic_trace_keeps_using_the_initial_graph_snapshot():
    initial_graph = DynamicGraph()
    initial_graph.add_edge("A", "B", 2.0)
    initial_graph.add_edge("B", "C", 1.0)
    initial_graph.add_edge("A", "C", 8.0)
    current_graph = DynamicGraph()
    current_graph.add_edge("A", "B", 2.0)
    current_graph.add_edge("B", "C", 1.0)
    current_graph.add_edge("A", "C", 8.0)
    state = SimpleNamespace(
        classic_graph=initial_graph,
        graph=current_graph,
        start_node=SimpleNamespace(get=lambda: "A"),
    )

    current_graph.update_weight("A", "C", 0.0)
    current_graph.remove_edge("B", "C")

    steps = TraceMixin._trace_classic(state)

    assert steps[0].updated_nodes == ("B", "C")
    assert steps[1].node == "B"
    assert steps[1].updated_nodes == ("C",)
