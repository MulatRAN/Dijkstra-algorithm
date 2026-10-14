# Dynamic Dijkstra Research Project

Research project exploring dynamic shortest path algorithms that efficiently maintain optimal paths under graph modifications.

## Project Structure

```
.
├── src/                    # Core implementation
│   ├── graph.py           # Dynamic graph data structure
│   ├── dijkstra.py        # Classic Dijkstra (baseline)
│   ├── dynamic_algo.py    # Dynamic shortest path algorithm
│   └── generator.py       # Test graph generators (alphabetic node labels)
├── experiments/           # Experimental framework
│   ├── scenarios.py       # Graph modification scenarios
│   └── benchmark.py       # Performance benchmarking
├── viz/                   # Visualization
│   └── plots.py          # Graph and result visualization
├── examples/              # Runnable learning examples
│   └── demo_dijkstra.py  # Dijkstra graph and distance plots
├── tests/                 # Unit tests
│   ├── test_graph.py
│   ├── test_dijkstra.py
│   └── test_generator.py
├── report/                # Research report
│   └── README.md         # Full report (FR)
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Interactive interface

From the project root, start the desktop app with:

```bash
python app.py
```

The app opens on the directed sample graph used in this README's basic example.
Choose an edge to change its weight, remove it, or add a directed edge. The graph
and shortest path update alongside a comparison of classic full recomputation
and the dynamic algorithm's incremental update.
Use the step-through controls to play, pause, or inspect each algorithm one
vertex at a time; the active node and affected vertices are highlighted on the
graph. The comparison also reports the latest measured runtime and trace
counters: finalized vertices and successful relaxations for classic Dijkstra,
and repaired vertices and changed `rhs` values for the dynamic algorithm.
These counters describe different kinds of work and should be interpreted
alongside the explanatory labels rather than as identical operations.

### Running Tests

```bash
pytest
```

### Basic Example

```python
from src.graph import DynamicGraph
from src.dijkstra import dijkstra
from src.dynamic_algo import DynamicDijkstra

# Create graph
graph = DynamicGraph()
graph.add_edge("A", "B", 4.0)
graph.add_edge("A", "C", 1.0)
graph.add_edge("C", "B", 2.0)

# Classic Dijkstra
distances, predecessors = dijkstra(graph, start="A")

# Dynamic algorithm
dyn = DynamicDijkstra(graph, start="A")
dyn.compute_shortest_paths()

# Modify graph and update
dyn.handle_edge_weight_change("A", "B", 10.0)
```

### See Dijkstra in action

From the project root, run:

```bash
python -m examples.demo_dijkstra
```

The example prints the shortest distances and route, then opens a graph with the
route highlighted and a chart of distances from the start node. Close the graph
window to see the distance chart.

### Running Benchmarks

```python
from src.generator import generate_random_graph
from experiments.scenarios import EdgeWeightIncrease, EdgeRemoval
from experiments.benchmark import Benchmark

# Generate test graph
graph = generate_random_graph(100, edge_probability=0.3, seed=42)

# Run benchmarks
benchmark = Benchmark()
scenarios = [EdgeWeightIncrease(), EdgeRemoval()]
results = benchmark.run_batch([(graph, "A", "AX")], scenarios, num_runs=10)

# Display results
benchmark.print_summary()
benchmark.export_csv('results.csv')
```

### Visualization

```python
from viz.plots import visualize_graph, plot_performance_comparison

# Visualize graph with path
visualize_graph(graph, path=["A", "C", "B"], title="Shortest Path")

# Plot benchmark results
plot_performance_comparison(results, title="Performance Comparison")
```

## Algorithms

### Classic Dijkstra
- Standard implementation with priority queue
- O((V + E) log V) complexity
- Full recomputation on every graph change

### Dynamic Algorithm
- Inspired by D* Lite and LPA*
- Maintains shortest paths incrementally
- Efficient updates on edge weight changes
- Avoids full recomputation

## Research Goals

1. Compare performance of dynamic vs. classic algorithms
2. Analyze speedup under various modification scenarios
3. Study scalability with graph size
4. Identify conditions where dynamic approaches excel

## Dependencies

- Python 3.8+
- NetworkX (graph algorithms)
- Matplotlib (visualization)
- pytest (testing)

## Contributing

This is a research project. Contributions welcome:
- Additional dynamic algorithms (incremental Bellman-Ford, etc.)
- More sophisticated scenarios
- Performance optimizations
- Extended benchmarks

## License

MIT License

## Authors

Research project for advanced algorithms course.

## References

1. Koenig, S., & Likhachev, M. (2002). D* Lite
2. Ramalingam, G., & Reps, T. (1996). Incremental shortest paths
3. Demetrescu, C., & Italiano, G. F. (2004). Dynamic all pairs shortest paths