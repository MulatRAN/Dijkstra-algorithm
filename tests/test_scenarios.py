"""Unit tests for graph modification scenarios."""

from experiments.scenarios import NodeAddition
from src.graph import DynamicGraph


def test_node_addition_uses_next_alphabetic_label():
    graph = DynamicGraph()
    for label in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        graph.add_node(label)

    new_node, _ = NodeAddition(num_edges=0).apply(graph)

    assert new_node == "AA"
    assert new_node in graph.nodes
