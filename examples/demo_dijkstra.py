"""Run a small Dijkstra example and display its graph and distances."""

from src.dijkstra import dijkstra, reconstruct_path
from src.graph import DynamicGraph
from viz.plots import plot_distances, visualize_graph


def main() -> None:
    graph = DynamicGraph()
    for source, dest, weight in [
        ("A", "B", 4.0),
        ("A", "C", 1.0),
        ("C", "B", 2.0),
        ("B", "D", 1.0),
        ("C", "D", 5.0),
        ("D", "E", 3.0),
        ("B", "E", 7.0),
    ]:
        graph.add_edge(source, dest, weight)

    start, target = "A", "E"
    distances, predecessors = dijkstra(graph, start)
    path = reconstruct_path(predecessors, start, target)

    print(f"Départ : {start}")
    print(f"Arrivée : {target}")
    print("\nDistances minimales depuis le départ :")
    for node, distance in sorted(distances.items()):
        print(f"  vers {node} : {distance:g}")

    print(f"\nChemin le plus court : {' -> '.join(map(str, path))}")
    print(f"Coût total : {distances[target]:g}")
    print("\nFerme la première fenêtre pour afficher la figure des distances.")

    visualize_graph(
        graph,
        path=path,
        title=f"Plus court chemin de {start} à {target} (coût {distances[target]:g})",
    )
    plot_distances(distances, title=f"Distances minimales depuis le nœud {start}")


if __name__ == "__main__":
    main()
