"""
Unit tests for dijkstra.py
"""
import pytest
from src.graph import DynamicGraph
from src.dijkstra import dijkstra, reconstruct_path


def test_dijkstra_simple():
    """Test Dijkstra on a simple graph"""
    graph = DynamicGraph()
    graph.add_edge(0, 1, 4.0)
    graph.add_edge(0, 2, 1.0)
    graph.add_edge(2, 1, 2.0)

    distances, predecessors = dijkstra(graph, 0)

    assert distances[0] == 0
    assert distances[1] == 3.0  # 0 -> 2 -> 1
    assert distances[2] == 1.0  # 0 -> 2


def test_dijkstra_no_path():
    """Test Dijkstra when no path exists"""
    graph = DynamicGraph()
    graph.add_node(0)
    graph.add_node(1)
    # No edges

    distances, predecessors = dijkstra(graph, 0)

    assert distances[0] == 0
    assert distances[1] == float('inf')


def test_reconstruct_path():
    """Test path reconstruction"""
    graph = DynamicGraph()
    graph.add_edge(0, 1, 1.0)
    graph.add_edge(1, 2, 1.0)

    distances, predecessors = dijkstra(graph, 0)
    path = reconstruct_path(predecessors, 0, 2)

    assert path == [0, 1, 2]


def test_dijkstra_with_target():
    """Test Dijkstra with specific target"""
    graph = DynamicGraph()
    graph.add_edge(0, 1, 1.0)
    graph.add_edge(1, 2, 1.0)
    graph.add_edge(2, 3, 1.0)

    distances, predecessors = dijkstra(graph, 0, end=2)

    assert distances[2] == 2.0
    # Should not compute to node 3 (early termination)
