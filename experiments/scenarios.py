"""
Dynamic Change Scenarios
Defines various graph modification scenarios for testing
"""
from typing import List, Tuple, Callable
import random
from src.graph import DynamicGraph


class ChangeScenario:
    """Base class for graph change scenarios"""

    def __init__(self, name: str):
        self.name = name

    def apply(self, graph: DynamicGraph) -> None:
        """Apply the scenario to the graph"""
        raise NotImplementedError


class EdgeWeightIncrease(ChangeScenario):
    """Increase weight of a random edge"""

    def __init__(self, increase_factor: float = 1.5):
        super().__init__(f"Edge Weight Increase (×{increase_factor})")
        self.increase_factor = increase_factor

    def apply(self, graph: DynamicGraph) -> Tuple[int, int, float, float]:
        """Returns (source, dest, old_weight, new_weight)"""
        # Find random edge
        nodes_with_edges = [n for n in graph.nodes if graph.get_neighbors(n)]
        if not nodes_with_edges:
            return None

        source = random.choice(nodes_with_edges)
        neighbors = graph.get_neighbors(source)
        dest, old_weight = random.choice(neighbors)

        new_weight = old_weight * self.increase_factor
        graph.update_weight(source, dest, new_weight)

        return source, dest, old_weight, new_weight


class EdgeWeightDecrease(ChangeScenario):
    """Decrease weight of a random edge"""

    def __init__(self, decrease_factor: float = 0.5):
        super().__init__(f"Edge Weight Decrease (×{decrease_factor})")
        self.decrease_factor = decrease_factor

    def apply(self, graph: DynamicGraph) -> Tuple[int, int, float, float]:
        """Returns (source, dest, old_weight, new_weight)"""
        nodes_with_edges = [n for n in graph.nodes if graph.get_neighbors(n)]
        if not nodes_with_edges:
            return None

        source = random.choice(nodes_with_edges)
        neighbors = graph.get_neighbors(source)
        dest, old_weight = random.choice(neighbors)

        new_weight = old_weight * self.decrease_factor
        graph.update_weight(source, dest, new_weight)

        return source, dest, old_weight, new_weight


class EdgeRemoval(ChangeScenario):
    """Remove a random edge from the graph"""

    def __init__(self):
        super().__init__("Edge Removal")

    def apply(self, graph: DynamicGraph) -> Tuple[int, int]:
        """Returns (source, dest)"""
        nodes_with_edges = [n for n in graph.nodes if graph.get_neighbors(n)]
        if not nodes_with_edges:
            return None

        source = random.choice(nodes_with_edges)
        neighbors = graph.get_neighbors(source)
        dest, _ = random.choice(neighbors)

        graph.remove_edge(source, dest)

        return source, dest


class EdgeAddition(ChangeScenario):
    """Add a new random edge to the graph"""

    def __init__(self, weight_range: Tuple[float, float] = (1.0, 10.0)):
        super().__init__("Edge Addition")
        self.weight_range = weight_range

    def apply(self, graph: DynamicGraph) -> Tuple[int, int, float]:
        """Returns (source, dest, weight)"""
        nodes = list(graph.nodes)
        if len(nodes) < 2:
            return None

        # Find non-existing edge
        max_attempts = 100
        for _ in range(max_attempts):
            source = random.choice(nodes)
            dest = random.choice([n for n in nodes if n != source])

            if graph.get_weight(source, dest) is None:
                weight = random.uniform(*self.weight_range)
                graph.add_edge(source, dest, weight)
                return source, dest, weight

        return None


class NodeAddition(ChangeScenario):
    """Add a new node with random edges"""

    def __init__(self, num_edges: int = 3, weight_range: Tuple[float, float] = (1.0, 10.0)):
        super().__init__(f"Node Addition ({num_edges} edges)")
        self.num_edges = num_edges
        self.weight_range = weight_range

    def apply(self, graph: DynamicGraph) -> Tuple[int, List[Tuple[int, float]]]:
        """Returns (new_node, [(dest, weight), ...])"""
        new_node = max(graph.nodes) + 1 if graph.nodes else 0
        graph.add_node(new_node)

        existing_nodes = [n for n in graph.nodes if n != new_node]
        if not existing_nodes:
            return new_node, []

        num_connections = min(self.num_edges, len(existing_nodes))
        targets = random.sample(existing_nodes, num_connections)

        edges = []
        for target in targets:
            weight = random.uniform(*self.weight_range)
            graph.add_edge(new_node, target, weight)
            edges.append((target, weight))

        return new_node, edges


class MultipleChanges(ChangeScenario):
    """Apply multiple changes in sequence"""

    def __init__(self, scenarios: List[ChangeScenario]):
        super().__init__(f"Multiple Changes ({len(scenarios)})")
        self.scenarios = scenarios

    def apply(self, graph: DynamicGraph) -> List:
        """Returns list of results from each scenario"""
        results = []
        for scenario in self.scenarios:
            result = scenario.apply(graph)
            results.append(result)
        return results
