"""
Unit tests for graph.py
"""
import pytest
from src.graph import DynamicGraph


def test_graph_creation():
    """Test basic graph creation"""
    graph = DynamicGraph()
    assert graph.get_node_count() == 0
    assert graph.get_edge_count() == 0


def test_add_node():
    """Test adding nodes"""
    graph = DynamicGraph()
    graph.add_node("A")
    graph.add_node("B")

    assert graph.get_node_count() == 2
    assert "A" in graph.nodes
    assert "B" in graph.nodes


def test_add_edge():
    """Test adding edges"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 5.0)

    assert graph.get_node_count() == 2
    assert graph.get_edge_count() == 1
    assert graph.get_weight("A", "B") == 5.0


def test_remove_edge():
    """Test removing edges"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 5.0)
    graph.remove_edge("A", "B")

    assert graph.get_edge_count() == 0
    assert graph.get_weight("A", "B") is None


def test_update_weight():
    """Test updating edge weights"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 5.0)
    graph.update_weight("A", "B", 10.0)

    assert graph.get_weight("A", "B") == 10.0


def test_remove_node():
    """Test removing nodes"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 5.0)
    graph.add_edge("B", "C", 3.0)
    graph.remove_node("B")

    assert "B" not in graph.nodes
    assert graph.get_node_count() == 2


def test_get_neighbors():
    """Test getting neighbors"""
    graph = DynamicGraph()
    graph.add_edge("A", "B", 5.0)
    graph.add_edge("A", "C", 3.0)

    neighbors = graph.get_neighbors("A")
    assert len(neighbors) == 2
    assert ("B", 5.0) in neighbors
    assert ("C", 3.0) in neighbors
