"""
Dynamic Shortest Path Algorithms
Maintains shortest paths incrementally after directed edge changes.
"""
import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .graph import DynamicGraph


@dataclass(frozen=True)
class DynamicStep:
    """One vertex processed while repairing the incremental shortest paths."""

    node: str
    old_distance: float
    new_distance: float
    rhs_value: float
    invalidated: bool
    updated_nodes: Tuple[str, ...]


class DynamicDijkstra:
    """Lifelong Planning A* style incremental single-source shortest paths."""

    def __init__(self, graph: DynamicGraph, start: str):
        if start not in graph.nodes:
            raise ValueError(f"Start node {start!r} is not in the graph")

        self.graph = graph
        self.start = start
        self.distances: Dict[str, float] = {}
        self.predecessors: Dict[str, Optional[str]] = {}
        self.g_values: Dict[str, float] = {}
        self.rhs_values: Dict[str, float] = {}
        self.open_list: List[Tuple[Tuple[float, float], str, int]] = []
        self._queue_versions: Dict[str, int] = {}
        self._queued: Set[str] = set()
        self.last_trace: List[DynamicStep] = []
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the LPA* state for every graph node."""
        self.g_values = {node: float("inf") for node in self.graph.nodes}
        self.rhs_values = {node: float("inf") for node in self.graph.nodes}
        self.predecessors = {node: None for node in self.graph.nodes}
        self._queue_versions = {node: 0 for node in self.graph.nodes}
        self._queued.clear()
        self.open_list.clear()
        self.rhs_values[self.start] = 0
        self._enqueue(self.start)

    def _calculate_key(self, node: str) -> Tuple[float, float]:
        value = min(self.g_values[node], self.rhs_values[node])
        return value, value

    def _enqueue(self, node: str) -> None:
        version = self._queue_versions.get(node, 0) + 1
        self._queue_versions[node] = version
        if self.g_values[node] != self.rhs_values[node]:
            heapq.heappush(
                self.open_list,
                (self._calculate_key(node), node, version),
            )
            self._queued.add(node)
        else:
            self._queued.discard(node)

    def _update_vertex(self, node: str) -> None:
        """Recalculate a vertex's one-step lookahead and queue membership."""
        if node not in self.graph.nodes:
            return
        if node not in self.g_values:
            self.g_values[node] = float("inf")
            self.rhs_values[node] = float("inf")
            self.predecessors[node] = None
            self._queue_versions[node] = 0

        if node == self.start:
            self.rhs_values[node] = 0
            self.predecessors[node] = None
        else:
            best_distance = float("inf")
            best_predecessor: Optional[str] = None
            for predecessor in sorted(self.graph.nodes):
                weight = self.graph.get_weight(predecessor, node)
                if weight is None:
                    continue
                candidate = self.g_values.get(predecessor, float("inf")) + weight
                if candidate < best_distance:
                    best_distance = candidate
                    best_predecessor = predecessor
            self.rhs_values[node] = best_distance
            self.predecessors[node] = best_predecessor

        self._enqueue(node)

    def compute_shortest_paths(self) -> None:
        """Process inconsistent vertices until all shortest paths are current."""
        self.last_trace = []
        while self.open_list:
            _, current, version = heapq.heappop(self.open_list)
            if version != self._queue_versions.get(current):
                continue
            self._queued.discard(current)

            old_distance = self.g_values[current]
            rhs_value = self.rhs_values[current]
            updated_nodes = []
            if self.g_values[current] > self.rhs_values[current]:
                self.g_values[current] = self.rhs_values[current]
                for neighbor, _ in self.graph.get_neighbors(current):
                    previous_rhs = self.rhs_values.get(neighbor, float("inf"))
                    self._update_vertex(neighbor)
                    if self.rhs_values[neighbor] != previous_rhs:
                        updated_nodes.append(neighbor)
                invalidated = False
            else:
                self.g_values[current] = float("inf")
                previous_rhs = self.rhs_values[current]
                self._update_vertex(current)
                if self.rhs_values[current] != previous_rhs:
                    updated_nodes.append(current)
                for neighbor, _ in self.graph.get_neighbors(current):
                    previous_rhs = self.rhs_values.get(neighbor, float("inf"))
                    self._update_vertex(neighbor)
                    if self.rhs_values[neighbor] != previous_rhs:
                        updated_nodes.append(neighbor)
                invalidated = True

            self.last_trace.append(
                DynamicStep(
                    node=current,
                    old_distance=old_distance,
                    new_distance=self.g_values[current],
                    rhs_value=rhs_value,
                    invalidated=invalidated,
                    updated_nodes=tuple(updated_nodes),
                )
            )

        self.distances = self.g_values.copy()

    def handle_edge_weight_change(
        self, source: str, dest: str, new_weight: Optional[float]
    ) -> None:
        """Add, update, or remove a directed edge and repair affected paths."""
        if source not in self.graph.nodes:
            self.graph.add_node(source)
            self._update_vertex(source)
        if dest not in self.graph.nodes:
            self.graph.add_node(dest)
            self._update_vertex(dest)

        old_weight = self.graph.get_weight(source, dest)
        if new_weight is None:
            self.graph.remove_edge(source, dest)
        elif old_weight != new_weight:
            self.graph.add_edge(source, dest, new_weight)

        if old_weight != new_weight:
            self._update_vertex(dest)
            self.compute_shortest_paths()

    def get_path(self, end: str) -> List[str]:
        """Reconstruct a shortest path from the start to ``end``."""
        if self.distances.get(end, float("inf")) == float("inf"):
            return []

        path = [end]
        visited = {end}
        current = end
        while current != self.start:
            predecessor = self.predecessors.get(current)
            if predecessor is None or predecessor in visited:
                return []
            path.append(predecessor)
            visited.add(predecessor)
            current = predecessor

        path.reverse()
        return path
