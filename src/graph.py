"""
Dynamic Graph Structure
Supports node and edge additions/removals, weight updates
"""
from typing import Dict, List, Set, Tuple, Optional


def alphabetic_label(index: int) -> str:
    """Convert a zero-based index to spreadsheet-style labels: A, ..., Z, AA, ..."""
    if index < 0:
        raise ValueError("index must be non-negative")

    label = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        label = chr(ord("A") + remainder) + label
    return label


def next_node_label(nodes: Set[str]) -> str:
    """Return the first available alphabetic node label."""
    index = 0
    while (label := alphabetic_label(index)) in nodes:
        index += 1
    return label


class DynamicGraph:
    """Graph structure supporting dynamic modifications"""

    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, List[Tuple[str, float]]] = {}

    def add_node(self, node: str) -> None:
        """Add a node to the graph"""
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = []

    def remove_node(self, node: str) -> None:
        """Remove a node and all its edges"""
        if node not in self.nodes:
            return

        self.nodes.remove(node)
        del self.edges[node]

        # Remove edges pointing to this node
        for source in self.edges:
            self.edges[source] = [
                (dest, weight) for dest, weight in self.edges[source] if dest != node
            ]

    def add_edge(self, source: str, dest: str, weight: float) -> None:
        """Add or update an edge with given weight"""
        if source not in self.nodes:
            self.add_node(source)
        if dest not in self.nodes:
            self.add_node(dest)

        # Remove existing edge if present
        self.edges[source] = [(d, w) for d, w in self.edges[source] if d != dest]
        # Add new edge
        self.edges[source].append((dest, weight))

    def remove_edge(self, source: str, dest: str) -> None:
        """Remove an edge from the graph"""
        if source in self.edges:
            self.edges[source] = [(d, w) for d, w in self.edges[source] if d != dest]

    def update_weight(self, source: str, dest: str, new_weight: float) -> None:
        """Update the weight of an existing edge"""
        if source not in self.edges:
            return

        for i, (d, w) in enumerate(self.edges[source]):
            if d == dest:
                self.edges[source][i] = (dest, new_weight)
                break

    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """Get all neighbors of a node with edge weights"""
        return self.edges.get(node, [])

    def get_weight(self, source: str, dest: str) -> Optional[float]:
        """Get weight of edge from source to dest"""
        for d, w in self.edges.get(source, []):
            if d == dest:
                return w
        return None

    def get_node_count(self) -> int:
        """Return number of nodes in graph"""
        return len(self.nodes)

    def get_edge_count(self) -> int:
        """Return number of edges in graph"""
        return sum(len(adj_list) for adj_list in self.edges.values())
