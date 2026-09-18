"""
Visualization and Plotting
Generate graphs and comparison plots for results
"""
import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict, Optional
from src.graph import DynamicGraph
from experiments.benchmark import BenchmarkResult


def visualize_graph(
    graph: DynamicGraph,
    path: Optional[List[int]] = None,
    title: str = "Graph Visualization",
    figsize: tuple = (10, 8)
) -> None:
    """
    Visualize a graph using matplotlib and networkx

    Args:
        graph: DynamicGraph to visualize
        path: Optional path to highlight
        title: Plot title
        figsize: Figure size
    """
    G = nx.DiGraph()

    # Add nodes
    for node in graph.nodes:
        G.add_node(node)

    # Add edges with weights
    edge_labels = {}
    for source in graph.nodes:
        for dest, weight in graph.get_neighbors(source):
            G.add_edge(source, dest)
            edge_labels[(source, dest)] = f"{weight:.1f}"

    plt.figure(figsize=figsize)
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes
    node_colors = ['lightblue'] * len(G.nodes())
    if path:
        for i, node in enumerate(G.nodes()):
            if node in path:
                node_colors[i] = 'lightgreen'

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500)
    nx.draw_networkx_labels(G, pos)

    # Draw edges
    edge_colors = ['black'] * len(G.edges())
    if path:
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        for i, edge in enumerate(G.edges()):
            if edge in path_edges:
                edge_colors[i] = 'red'

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowsize=20)
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def plot_performance_comparison(
    results: List[BenchmarkResult],
    title: str = "Performance Comparison",
    save_path: Optional[str] = None
) -> None:
    """
    Plot performance comparison between classic and dynamic algorithms

    Args:
        results: List of benchmark results
        title: Plot title
        save_path: Optional path to save figure
    """
    scenarios = [r.scenario_name for r in results]
    classic_times = [r.classic_time * 1000 for r in results]  # Convert to ms
    dynamic_times = [r.dynamic_time * 1000 for r in results]

    x = range(len(scenarios))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))

    bars1 = ax.bar([i - width/2 for i in x], classic_times, width, label='Classic Dijkstra')
    bars2 = ax.bar([i + width/2 for i in x], dynamic_times, width, label='Dynamic Algorithm')

    ax.set_xlabel('Scenario')
    ax.set_ylabel('Time (ms)')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def plot_speedup_chart(
    results: List[BenchmarkResult],
    title: str = "Speedup Factor",
    save_path: Optional[str] = None
) -> None:
    """
    Plot speedup factors for different scenarios

    Args:
        results: List of benchmark results
        title: Plot title
        save_path: Optional path to save figure
    """
    scenarios = [r.scenario_name for r in results]
    speedups = [r.speedup for r in results]

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['green' if s > 1 else 'red' for s in speedups]
    bars = ax.bar(range(len(scenarios)), speedups, color=colors)

    ax.axhline(y=1, color='black', linestyle='--', label='No speedup')
    ax.set_xlabel('Scenario')
    ax.set_ylabel('Speedup Factor')
    ax.set_title(title)
    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels(scenarios, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def plot_scaling_analysis(
    results_by_size: Dict[int, List[BenchmarkResult]],
    title: str = "Scaling Analysis",
    save_path: Optional[str] = None
) -> None:
    """
    Plot how algorithms scale with graph size

    Args:
        results_by_size: Dict mapping graph size to results
        title: Plot title
        save_path: Optional path to save figure
    """
    sizes = sorted(results_by_size.keys())
    classic_means = []
    dynamic_means = []

    for size in sizes:
        results = results_by_size[size]
        classic_means.append(sum(r.classic_time for r in results) / len(results) * 1000)
        dynamic_means.append(sum(r.dynamic_time for r in results) / len(results) * 1000)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(sizes, classic_means, 'o-', label='Classic Dijkstra', linewidth=2)
    ax.plot(sizes, dynamic_means, 's-', label='Dynamic Algorithm', linewidth=2)

    ax.set_xlabel('Graph Size (nodes)')
    ax.set_ylabel('Average Time (ms)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
