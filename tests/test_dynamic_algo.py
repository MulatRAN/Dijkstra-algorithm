"""Unit tests for the dynamic shortest-path algorithm."""

from src.dynamic_algo import DynamicDijkstra
from src.graph import DynamicGraph


def test_dynamic_dijkstra_works_with_alphabetic_nodes():
    graph = DynamicGraph()
    graph.add_edge("A", "B", 4.0)
    graph.add_edge("A", "C", 1.0)
    graph.add_edge("C", "B", 2.0)

    dynamic = DynamicDijkstra(graph, "A")
    dynamic.compute_shortest_paths()

    assert dynamic.distances["B"] == 3.0
    assert dynamic.get_path("B") == ["A", "C", "B"]


def test_dynamic_dijkstra_matches_classic_after_edge_changes():
    from src.dijkstra import dijkstra

    graph = DynamicGraph()
    for source, dest, weight in [
        ("A", "B", 4.0),
        ("A", "C", 1.0),
        ("C", "B", 2.0),
        ("B", "D", 1.0),
        ("C", "D", 5.0),
    ]:
        graph.add_edge(source, dest, weight)

    dynamic = DynamicDijkstra(graph, "A")
    dynamic.compute_shortest_paths()

    changes = [
        ("A", "B", 10.0),
        ("A", "D", 2.0),
        ("C", "B", None),
        ("A", "D", None),
        ("C", "D", 0.0),
    ]
    for source, dest, weight in changes:
        dynamic.handle_edge_weight_change(source, dest, weight)
        expected_distances, _ = dijkstra(graph, "A")
        assert dynamic.distances == expected_distances


def test_dynamic_dijkstra_records_incremental_repair_steps():
    graph = DynamicGraph()
    graph.add_edge("A", "B", 5.0)
    graph.add_edge("A", "C", 1.0)
    graph.add_edge("C", "B", 1.0)
    graph.add_edge("B", "D", 1.0)

    dynamic = DynamicDijkstra(graph, "A")
    dynamic.compute_shortest_paths()
    assert dynamic.last_trace
    assert dynamic.last_trace[0].node == "A"

    dynamic.handle_edge_weight_change("C", "B", 10.0)

    assert dynamic.distances["B"] == 5.0
    assert dynamic.last_trace
    assert any(step.node == "B" for step in dynamic.last_trace)
