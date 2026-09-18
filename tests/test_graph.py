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
    graph.add_node(1)
    graph.add_node(2)

    assert graph.get_node_count() == 2
    assert 1 in graph.nodes
    assert 2 in graph.nodes


def test_add_edge():
    """Test adding edges"""
    graph = DynamicGraph()
    graph.add_edge(1, 2, 5.0)

    assert graph.get_node_count() == 2
    assert graph.get_edge_count() == 1
    assert graph.get_weight(1, 2) == 5.0


def test_remove_edge():
    """Test removing edges"""
    graph = DynamicGraph()
    graph.add_edge(1, 2, 5.0)
    graph.remove_edge(1, 2)

    assert graph.get_edge_count() == 0
    assert graph.get_weight(1, 2) is None


def test_update_weight():
    """Test updating edge weights"""
    graph = DynamicGraph()
    graph.add_edge(1, 2, 5.0)
    graph.update_weight(1, 2, 10.0)

    assert graph.get_weight(1, 2) == 10.0


def test_remove_node():
    """Test removing nodes"""
    graph = DynamicGraph()
    graph.add_edge(1, 2, 5.0)
    graph.add_edge(2, 3, 3.0)
    graph.remove_node(2)

    assert 2 not in graph.nodes
    assert graph.get_node_count() == 2


def test_get_neighbors():
    """Test getting neighbors"""
    graph = DynamicGraph()
    graph.add_edge(1, 2, 5.0)
    graph.add_edge(1, 3, 3.0)

    neighbors = graph.get_neighbors(1)
    assert len(neighbors) == 2
    assert (2, 5.0) in neighbors
    assert (3, 3.0) in neighbors
