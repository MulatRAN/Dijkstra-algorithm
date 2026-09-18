"""
Dynamic Shortest Path Algorithms
Implements incremental updates without full recomputation
"""
from typing import Dict, List, Tuple, Optional, Set
import heapq
from .graph import DynamicGraph


class DynamicDijkstra:
    """
    Dynamic shortest path algorithm
    Maintains shortest paths efficiently under graph modifications
    Inspired by D* Lite and LPA* approaches
    """

    def __init__(self, graph: DynamicGraph, start: int):
        self.graph = graph
        self.start = start
        self.distances: Dict[int, float] = {}
        self.predecessors: Dict[int, Optional[int]] = {}
        self.g_values: Dict[int, float] = {}  # Current best distances
        self.rhs_values: Dict[int, float] = {}  # One-step lookahead values
        self.open_list: List[Tuple[Tuple[float, float], int]] = []
        self._initialize()

    def _initialize(self) -> None:
        """Initialize data structures"""
        for node in self.graph.nodes:
            self.g_values[node] = float('inf')
            self.rhs_values[node] = float('inf')
            self.predecessors[node] = None

        self.rhs_values[self.start] = 0
        self.open_list = []
        heapq.heappush(self.open_list, (self._calculate_key(self.start), self.start))

    def _calculate_key(self, node: int) -> Tuple[float, float]:
        """Calculate priority key for node (similar to LPA*)"""
        g = self.g_values[node]
        rhs = self.rhs_values[node]
        return (min(g, rhs), min(g, rhs))

    def _update_vertex(self, node: int) -> None:
        """Update vertex and priority queue"""
        if node != self.start:
            # Update rhs value based on predecessors
            min_rhs = float('inf')
            for pred in self.graph.nodes:
                weight = self.graph.get_weight(pred, node)
                if weight is not None:
                    candidate = self.g_values[pred] + weight
                    if candidate < min_rhs:
                        min_rhs = candidate
            self.rhs_values[node] = min_rhs

        # Remove from open list if present (simplified approach)
        if self.g_values[node] != self.rhs_values[node]:
            heapq.heappush(self.open_list, (self._calculate_key(node), node))

    def compute_shortest_paths(self) -> None:
        """Compute or update shortest paths"""
        while self.open_list:
            _, current = heapq.heappop(self.open_list)

            if self.g_values[current] > self.rhs_values[current]:
                # Vertex is locally inconsistent - update
                self.g_values[current] = self.rhs_values[current]

                # Update successors
                for neighbor, _ in self.graph.get_neighbors(current):
                    self._update_vertex(neighbor)
            else:
                # Vertex is locally overconsistent
                self.g_values[current] = float('inf')
                self._update_vertex(current)

                # Update successors
                for neighbor, _ in self.graph.get_neighbors(current):
                    self._update_vertex(neighbor)

        self.distances = self.g_values.copy()

    def handle_edge_weight_change(self, source: int, dest: int, new_weight: Optional[float]) -> None:
        """
        Handle edge weight change or edge removal

        Args:
            source: Source node
            dest: Destination node
            new_weight: New weight (None for edge removal)
        """
        if new_weight is None:
            self.graph.remove_edge(source, dest)
        else:
            old_weight = self.graph.get_weight(source, dest)
            if old_weight != new_weight:
                self.graph.update_weight(source, dest, new_weight)

        # Update affected vertices
        self._update_vertex(dest)

        # Recompute paths
        self.compute_shortest_paths()

    def get_path(self, end: int) -> List[int]:
        """Reconstruct path from start to end"""
        if self.distances.get(end, float('inf')) == float('inf'):
            return []

        path = [end]
        current = end

        while current != self.start:
            # Find best predecessor
            best_pred = None
            best_dist = float('inf')

            for node in self.graph.nodes:
                weight = self.graph.get_weight(node, current)
                if weight is not None:
                    dist = self.g_values[node] + weight
                    if dist < best_dist:
                        best_dist = dist
                        best_pred = node

            if best_pred is None:
                return []

            path.append(best_pred)
            current = best_pred

        path.reverse()
        return path
