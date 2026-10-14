from src.graph import DynamicGraph
from src.dijkstra import dijkstra, reconstruct_path
from src.dynamic_algo import DynamicDijkstra


def afficher_resultats(titre, graph, start, end, dynamique):
    distances_classique, predecesseurs_classique = dijkstra(graph, start, end)
    chemin_classique = reconstruct_path(predecesseurs_classique, start, end)

    print(f"\n{titre}")
    print("classique:")
    print(f"  chemin: {chemin_classique}")
    print(f"  distance: {distances_classique[end]}")

    print("dynamique:")
    print(f"  chemin: {dynamique.get_path(end)}")
    print(f"  distance: {dynamique.distances[end]}")


def main():
    start = "S"
    end = "T"

    graph = DynamicGraph()
    for node in ["S", "A", "B", "T"]:
        graph.add_node(node)

    graph.add_edge("S", "B", 1)
    graph.add_edge("S", "A", 2)
    graph.add_edge("B", "T", 3)
    graph.add_edge("A", "T", 3)

    dynamique = DynamicDijkstra(graph, start)
    dynamique.compute_shortest_paths()

    afficher_resultats(
        "Test 1 - calcul initial, sans changement du graphe",
        graph,
        start,
        end,
        dynamique,
    )

    print("\nModification pendant le scénario: le poids de B -> T passe de 3 à 4.")
    dynamique.handle_edge_weight_change("B", "T", 4)

    # Le classique ne conserve pas d'etat incremental : on le relance depuis start.
    afficher_resultats(
        "Test 2 - apres modification du poids",
        graph,
        start,
        end,
        dynamique,
    )


if __name__ == "__main__":
    main()
