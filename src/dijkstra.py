"""
Classic Dijkstra's Algorithm Implementation
Baseline for performance comparison
"""
import heapq
from typing import Dict, List, Tuple, Optional
from .graph import DynamicGraph


def dijkstra(graph: DynamicGraph, start: int, end: Optional[int] = None) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Classic Dijkstra's shortest path algorithm

    Args:
        graph: DynamicGraph instance
        start: Starting node
        end: Optional target node (if None, compute to all nodes)

    Returns:
        distances: Dict mapping node to shortest distance from start
        predecessors: Dict mapping node to predecessor in shortest path
    """
    distances: Dict[int, float] = {node: float('inf') for node in graph.nodes}
    predecessors: Dict[int, Optional[int]] = {node: None for node in graph.nodes}
    distances[start] = 0

    # Priority queue: (distance, node)
    pq = [(0, start)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue

        visited.add(current)

        # Early termination if target reached
        if end is not None and current == end:
            break

        # Skip if we've found a better path already
        if current_dist > distances[current]:
            continue

        # Check all neighbors
        for neighbor, weight in graph.get_neighbors(current):
            distance = current_dist + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))

    return distances, predecessors


def reconstruct_path(predecessors: Dict[int, Optional[int]], start: int, end: int) -> List[int]:
    """
    Reconstruct path from start to end using predecessors

    Args:
        predecessors: Dict from dijkstra output
        start: Starting node
        end: Ending node

    Returns:
        List of nodes in path from start to end
    """
    if predecessors[end] is None and start != end:
        return []  # No path exists

    path = []
    current = end

    while current is not None:
        path.append(current)
        current = predecessors[current]

    path.reverse()
    return path
