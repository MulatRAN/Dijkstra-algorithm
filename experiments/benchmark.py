"""
Performance Benchmarking
Compares classic Dijkstra vs dynamic algorithms under various scenarios
"""
import time
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass
import statistics

from src.graph import DynamicGraph
from src.dijkstra import dijkstra
from src.dynamic_algo import DynamicDijkstra
from experiments.scenarios import ChangeScenario


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    scenario_name: str
    graph_size: int
    edge_count: int
    classic_time: float
    dynamic_time: float
    speedup: float
    num_changes: int


class Benchmark:
    """Benchmark framework for comparing algorithms"""

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def run_scenario(
        self,
        graph: DynamicGraph,
        scenario: ChangeScenario,
        start_node: int,
        target_node: int,
        num_runs: int = 10
    ) -> BenchmarkResult:
        """
        Run a benchmark scenario comparing classic vs dynamic Dijkstra

        Args:
            graph: Initial graph
            scenario: Change scenario to apply
            start_node: Source node
            target_node: Target node
            num_runs: Number of runs for averaging

        Returns:
            BenchmarkResult with timing comparisons
        """
        classic_times = []
        dynamic_times = []

        for _ in range(num_runs):
            # Create copy for classic approach
            test_graph = self._copy_graph(graph)

            # Apply scenario
            scenario.apply(test_graph)

            # Measure classic Dijkstra (full recomputation)
            start_time = time.perf_counter()
            dijkstra(test_graph, start_node, target_node)
            classic_time = time.perf_counter() - start_time
            classic_times.append(classic_time)

            # Measure dynamic algorithm
            test_graph2 = self._copy_graph(graph)
            dynamic_dijkstra = DynamicDijkstra(test_graph2, start_node)
            dynamic_dijkstra.compute_shortest_paths()

            start_time = time.perf_counter()
            scenario.apply(test_graph2)
            dynamic_dijkstra.compute_shortest_paths()
            dynamic_time = time.perf_counter() - start_time
            dynamic_times.append(dynamic_time)

        avg_classic = statistics.mean(classic_times)
        avg_dynamic = statistics.mean(dynamic_times)
        speedup = avg_classic / avg_dynamic if avg_dynamic > 0 else 0

        result = BenchmarkResult(
            scenario_name=scenario.name,
            graph_size=graph.get_node_count(),
            edge_count=graph.get_edge_count(),
            classic_time=avg_classic,
            dynamic_time=avg_dynamic,
            speedup=speedup,
            num_changes=1
        )

        self.results.append(result)
        return result

    def _copy_graph(self, graph: DynamicGraph) -> DynamicGraph:
        """Create a deep copy of a graph"""
        new_graph = DynamicGraph()
        for node in graph.nodes:
            new_graph.add_node(node)

        for source in graph.nodes:
            for dest, weight in graph.get_neighbors(source):
                new_graph.add_edge(source, dest, weight)

        return new_graph

    def run_batch(
        self,
        graphs: List[Tuple[DynamicGraph, int, int]],
        scenarios: List[ChangeScenario],
        num_runs: int = 10
    ) -> List[BenchmarkResult]:
        """
        Run multiple scenarios on multiple graphs

        Args:
            graphs: List of (graph, start_node, target_node) tuples
            scenarios: List of scenarios to test
            num_runs: Number of runs per scenario

        Returns:
            List of all benchmark results
        """
        results = []

        for i, (graph, start, target) in enumerate(graphs):
            print(f"Testing graph {i+1}/{len(graphs)} (nodes={graph.get_node_count()}, edges={graph.get_edge_count()})")

            for scenario in scenarios:
                print(f"  Scenario: {scenario.name}")
                result = self.run_scenario(graph, scenario, start, target, num_runs)
                results.append(result)
                print(f"    Classic: {result.classic_time*1000:.3f}ms, Dynamic: {result.dynamic_time*1000:.3f}ms, Speedup: {result.speedup:.2f}x")

        return results

    def print_summary(self) -> None:
        """Print summary of all benchmark results"""
        if not self.results:
            print("No benchmark results available")
            return

        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)

        for result in self.results:
            print(f"\nScenario: {result.scenario_name}")
            print(f"  Graph: {result.graph_size} nodes, {result.edge_count} edges")
            print(f"  Classic Dijkstra: {result.classic_time*1000:.3f} ms")
            print(f"  Dynamic Algorithm: {result.dynamic_time*1000:.3f} ms")
            print(f"  Speedup: {result.speedup:.2f}x")

        avg_speedup = statistics.mean([r.speedup for r in self.results])
        print(f"\nAverage Speedup: {avg_speedup:.2f}x")
        print("="*80)

    def export_csv(self, filename: str) -> None:
        """Export results to CSV file"""
        import csv

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Scenario', 'Graph Size', 'Edge Count',
                'Classic Time (ms)', 'Dynamic Time (ms)', 'Speedup'
            ])

            for result in self.results:
                writer.writerow([
                    result.scenario_name,
                    result.graph_size,
                    result.edge_count,
                    f"{result.classic_time*1000:.3f}",
                    f"{result.dynamic_time*1000:.3f}",
                    f"{result.speedup:.2f}"
                ])
