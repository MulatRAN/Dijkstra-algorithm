"""
Random Graph Generator
Creates test graphs with various properties for benchmarking
"""
import random
from typing import Tuple
from .graph import DynamicGraph


def generate_random_graph(
    num_nodes: int,
    edge_probability: float = 0.3,
    min_weight: float = 1.0,
    max_weight: float = 10.0,
    seed: int = None
) -> DynamicGraph:
    """
    Generate a random directed graph

    Args:
        num_nodes: Number of nodes
        edge_probability: Probability of edge between any two nodes
        min_weight: Minimum edge weight
        max_weight: Maximum edge weight
        seed: Random seed for reproducibility

    Returns:
        DynamicGraph instance
    """
    if seed is not None:
        random.seed(seed)

    graph = DynamicGraph()

    # Add all nodes
    for i in range(num_nodes):
        graph.add_node(i)

    # Add random edges
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j and random.random() < edge_probability:
                weight = random.uniform(min_weight, max_weight)
                graph.add_edge(i, j, weight)

    return graph


def generate_grid_graph(rows: int, cols: int, weight_range: Tuple[float, float] = (1.0, 10.0)) -> DynamicGraph:
    """
    Generate a grid graph (useful for pathfinding scenarios)

    Args:
        rows: Number of rows
        cols: Number of columns
        weight_range: (min, max) weight range

    Returns:
        DynamicGraph instance
    """
    graph = DynamicGraph()

    def node_id(r: int, c: int) -> int:
        return r * cols + c

    # Add nodes and edges
    for r in range(rows):
        for c in range(cols):
            current = node_id(r, c)
            graph.add_node(current)

            # Add edges to neighbors (4-connected)
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbor = node_id(nr, nc)
                    weight = random.uniform(*weight_range)
                    graph.add_edge(current, neighbor, weight)

    return graph


def generate_sparse_graph(num_nodes: int, avg_degree: int = 4, weight_range: Tuple[float, float] = (1.0, 10.0)) -> DynamicGraph:
    """
    Generate a sparse graph with controlled average degree

    Args:
        num_nodes: Number of nodes
        avg_degree: Average out-degree per node
        weight_range: (min, max) weight range

    Returns:
        DynamicGraph instance
    """
    graph = DynamicGraph()

    for i in range(num_nodes):
        graph.add_node(i)

    # Each node gets approximately avg_degree outgoing edges
    for i in range(num_nodes):
        num_edges = max(1, int(random.gauss(avg_degree, avg_degree / 3)))
        num_edges = min(num_edges, num_nodes - 1)

        targets = random.sample([j for j in range(num_nodes) if j != i], num_edges)
        for target in targets:
            weight = random.uniform(*weight_range)
            graph.add_edge(i, target, weight)

    return graph
