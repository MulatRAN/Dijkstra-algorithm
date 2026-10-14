"""Sample graph construction and graph-copy helpers for the interface."""

from src.graph import DynamicGraph

from .constants import DEMO_CONNECTIONS


def build_demo_graph() -> DynamicGraph:
    """Build the directed graph used in the project's README example."""
    graph = DynamicGraph()
    for source, dest, weight in DEMO_CONNECTIONS:
        graph.add_edge(source, dest, weight)
    return graph

def copy_graph(graph: DynamicGraph) -> DynamicGraph:
    """Make an independent graph copy for the dynamic algorithm."""
    copied = DynamicGraph()
    for node in graph.nodes:
        copied.add_node(node)
    for source in graph.nodes:
        for dest, weight in graph.get_neighbors(source):
            copied.add_edge(source, dest, weight)
    return copied
