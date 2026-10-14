"""Compatibility entry point for the Dijkstra Lab desktop application."""

from ui.app import DijkstraLab, main
from ui.graph_data import build_demo_graph, copy_graph

if __name__ == "__main__":
    main()
