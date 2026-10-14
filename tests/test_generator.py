"""
Unit tests for generator.py
"""
import pytest
from src.generator import generate_random_graph, generate_grid_graph, generate_sparse_graph
from src.graph import alphabetic_label


def test_random_graph_generation():
    """Test random graph generation"""
    graph = generate_random_graph(10, edge_probability=0.3, seed=42)

    assert graph.get_node_count() == 10
    assert graph.get_edge_count() > 0
    assert graph.nodes == {chr(ord("A") + i) for i in range(10)}


def test_grid_graph_generation():
    """Test grid graph generation"""
    graph = generate_grid_graph(3, 3)

    assert graph.get_node_count() == 9
    assert graph.nodes == set("ABCDEFGHI")
    # Each internal node has 4 neighbors, edge nodes have 2-3
    assert graph.get_edge_count() > 0


def test_sparse_graph_generation():
    """Test sparse graph generation"""
    graph = generate_sparse_graph(20, avg_degree=4)

    assert graph.get_node_count() == 20
    avg_degree = graph.get_edge_count() / graph.get_node_count()
    assert 2 <= avg_degree <= 6  # Should be roughly 4


def test_alphabetic_labels_continue_after_z():
    assert [alphabetic_label(i) for i in (0, 25, 26, 27, 51, 52)] == [
        "A",
        "Z",
        "AA",
        "AB",
        "AZ",
        "BA",
    ]
