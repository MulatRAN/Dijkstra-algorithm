# Dynamic Dijkstra Research Project

Research project exploring dynamic shortest path algorithms that efficiently maintain optimal paths under graph modifications.

## Project Structure

```
.
├── src/                    # Core implementation
│   ├── graph.py           # Dynamic graph data structure
│   ├── dijkstra.py        # Classic Dijkstra (baseline)
│   ├── dynamic_algo.py    # Dynamic shortest path algorithm
│   └── generator.py       # Test graph generators
├── experiments/           # Experimental framework
│   ├── scenarios.py       # Graph modification scenarios
│   └── benchmark.py       # Performance benchmarking
├── viz/                   # Visualization
│   └── plots.py          # Graph and result visualization
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
graph.add_edge(0, 1, 4.0)
graph.add_edge(0, 2, 1.0)
graph.add_edge(2, 1, 2.0)

# Classic Dijkstra
distances, predecessors = dijkstra(graph, start=0)

# Dynamic algorithm
dyn = DynamicDijkstra(graph, start=0)
dyn.compute_shortest_paths()

# Modify graph and update
dyn.handle_edge_weight_change(0, 1, 10.0)
```

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
results = benchmark.run_batch([(graph, 0, 50)], scenarios, num_runs=10)

# Display results
benchmark.print_summary()
benchmark.export_csv('results.csv')
```

### Visualization

```python
from viz.plots import visualize_graph, plot_performance_comparison

# Visualize graph with path
visualize_graph(graph, path=[0, 2, 1], title="Shortest Path")

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