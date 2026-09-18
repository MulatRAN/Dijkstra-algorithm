"""
Unit tests for generator.py
"""
import pytest
from src.generator import generate_random_graph, generate_grid_graph, generate_sparse_graph


def test_random_graph_generation():
    """Test random graph generation"""
    graph = generate_random_graph(10, edge_probability=0.3, seed=42)

    assert graph.get_node_count() == 10
    assert graph.get_edge_count() > 0


def test_grid_graph_generation():
    """Test grid graph generation"""
    graph = generate_grid_graph(3, 3)

    assert graph.get_node_count() == 9
    # Each internal node has 4 neighbors, edge nodes have 2-3
    assert graph.get_edge_count() > 0


def test_sparse_graph_generation():
    """Test sparse graph generation"""
    graph = generate_sparse_graph(20, avg_degree=4)

    assert graph.get_node_count() == 20
    avg_degree = graph.get_edge_count() / graph.get_node_count()
    assert 2 <= avg_degree <= 6  # Should be roughly 4
