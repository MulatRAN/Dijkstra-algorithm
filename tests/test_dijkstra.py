"""
Unit tests for dijkstra.py
"""
import pytest
import src.dijkstra as dijkstra_module
from src.graph import DynamicGraph
from src.dijkstra import dijkstra, reconstruct_path


def test_dijkstra_simple():
    """Test Dijkstra on a simple graph"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 4.0)
    graph.add_edge("A", "C", 1.0)
    graph.add_edge("C", "B", 2.0)

    distances, predecessors = dijkstra(graph, "A")

    assert distances["A"] == 0
    assert distances["B"] == 3.0  # A -> C -> B
    assert distances["C"] == 1.0  # A -> C


def test_dijkstra_no_path():
    """Test Dijkstra when no path exists"""
    graph = DynamicGraph()
    graph.add_node("A")
    graph.add_node("B")
    # No edges

    distances, predecessors = dijkstra(graph, "A")

    assert distances["A"] == 0
    assert distances["B"] == float('inf')


def test_reconstruct_path():
    """Test path reconstruction"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 1.0)
    graph.add_edge("B", "C", 1.0)

    distances, predecessors = dijkstra(graph, "A")
    path = reconstruct_path(predecessors, "A", "C")

    assert path == ["A", "B", "C"]


def test_dijkstra_with_target():
    """Test Dijkstra with specific target"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 1.0)
    graph.add_edge("B", "C", 1.0)
    graph.add_edge("C", "D", 1.0)

    distances, predecessors = dijkstra(graph, "A", end="C")

    assert distances["C"] == 2.0
    # Should not compute to node 3 (early termination)


def test_dijkstra_uses_graph_snapshot_taken_before_traversal(monkeypatch):
    """Graph changes after the search starts must not affect its result."""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 2.0)
    graph.add_edge("B", "C", 2.0)
    graph.add_edge("A", "C", 10.0)

    original_heappop = dijkstra_module.heapq.heappop
    changed = False

    def mutate_graph_after_snapshot(queue):
        nonlocal changed
        if not changed:
            changed = True
            graph.update_weight("A", "C", 1.0)
            graph.remove_edge("B", "C")
            graph.add_edge("A", "D", 1.0)
        return original_heappop(queue)

    monkeypatch.setattr(dijkstra_module.heapq, "heappop", mutate_graph_after_snapshot)

    distances, predecessors = dijkstra(graph, "A")

    assert distances == {"A": 0, "B": 2.0, "C": 4.0}
    assert predecessors["C"] == "B"
    assert "D" not in distances
