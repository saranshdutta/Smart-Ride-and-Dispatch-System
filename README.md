
# 🚗 Smart Ride Matching & Dispatch System

> A production-quality, full-stack ride-hailing simulation platform demonstrating three algorithmic approaches to driver–passenger matching, built for FAANG-level portfolio quality.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Algorithms](#algorithms)
- [Complexity Analysis](#complexity-analysis)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Benchmarking](#benchmarking)
- [Design Patterns](#design-patterns)
- [Tech Stack](#tech-stack)

---

## Overview

Smart Dispatch simulates a real-world ride-hailing platform where passengers are matched to the nearest available driver. It is designed to compare three algorithmic strategies — **Greedy**, **Heap (Priority Queue)**, and **Dijkstra (Graph Routing)** — across fleet sizes of varying scale, with real-time metrics and a live dashboard.

---

## Features

| Feature | Details |
|---|---|
| **3 Matching Algorithms** | Greedy · Min-Heap · Dijkstra |
| **Strategy Pattern** | Hot-swap algorithm at runtime |
| **FastAPI Backend** | RESTful JSON API with Swagger docs |
| **Premium Dashboard** | Dark glassmorphism UI · Canvas map · Chart.js |
| **Benchmarking Suite** | Multi-scenario CLI comparison across fleet sizes |
| **Unit Tests** | 25+ test cases with pytest, fully parametrized |
| **Seeded Simulation** | Reproducible random generation for deterministic benchmarks |
| **Haversine Distance** | Real-world geographic distance calculations (km) |

---

## Architecture

```
Smart Dispatch/
├── models/
│   ├── driver.py          # Driver dataclass — location, availability, rating
│   ├── passenger.py       # Passenger dataclass — pickup/dropoff, match state
│   └── trip.py            # Trip result — driver+passenger+route+distance
│
├── algorithms/
│   ├── base.py            # Abstract MatchingAlgorithm (Strategy interface)
│   ├── greedy.py          # O(P×D) nearest-driver linear scan
│   ├── heap_match.py      # O((D+P)logD) min-heap optimization
│   └── dijkstra.py        # O(P·(V+E)logV) graph-based routing
│
├── system/
│   ├── dispatcher.py      # Strategy-pattern dispatcher with algorithm registry
│   └── simulator.py       # Simulation orchestrator — generate + dispatch + report
│
├── utils/
│   ├── distance.py        # Haversine, Euclidean, Manhattan distance functions
│   ├── metrics.py         # MetricsCollector — time, match rate, distance stats
│   └── config.py          # SimulationConfig — validated parameter container
│
├── api/
│   ├── main.py            # FastAPI app — CORS, static file serving, health check
│   └── routes.py          # /simulate, /drivers, /passengers, /metrics, /benchmark
│
├── frontend/
│   ├── index.html         # Dashboard HTML — controls, stats, map, charts
│   ├── style.css          # Premium dark glassmorphism design system
│   └── app.js             # Canvas map, Chart.js, API calls, animations
│
├── benchmark/
│   └── run_benchmark.py   # Multi-scenario comparison across 6 fleet sizes
│
├── tests/
│   ├── test_models.py     # Driver, Passenger, Trip unit tests
│   ├── test_algorithms.py # All 3 algorithms — parametrized test suite
│   └── test_dispatcher.py # Dispatcher strategy + Simulator integration tests
│
├── main.py                # CLI entry point
├── pytest.ini
└── requirements.txt
```

---

## Algorithms

### 1. Greedy — Nearest Driver Selection

For each passenger (FIFO order), scan all available drivers and pick the one with minimum Haversine distance. Simple, fast, zero preprocessing.

```python
for passenger in passengers:
    best = min(available_drivers, key=lambda d: haversine(passenger, d))
    assign(best, passenger)
```

**Best for:** Small fleets, latency-sensitive matching with minimal infrastructure.

---

### 2. Heap — Priority Queue Optimization

Pre-heapify all available drivers by distance for each passenger, then `heappop()` in O(log D) time. Eliminates the O(D) inner scan.

```python
heap = [(haversine(p, d), d.id) for d in available_drivers]
heapq.heapify(heap)
best_dist, best_id = heapq.heappop(heap)
```

**Best for:** Large fleets (200+ drivers) where per-passenger savings accumulate.

---

### 3. Dijkstra — Graph-Based Routing

Builds a k-nearest-neighbor road-network graph from all node positions, then runs Dijkstra's SSSP from each passenger's pickup node to find the shortest road-network distance to every available driver.

```
Graph: nodes = driver positions + pickup/dropoff positions
Edges: each node → k nearest neighbors (simulated roads)
SSSP:  Dijkstra from pickup_node → min road dist to any driver
```

**Best for:** Applications requiring realistic road-aware routing rather than straight-line distances.

---

## Complexity Analysis

| Algorithm | Time Complexity | Space Complexity | Preprocessing |
|---|---|---|---|
| **Greedy** | O(P × D) | O(1) | None |
| **Heap** | O((D + P) log D) | O(D) | None |
| **Dijkstra** | O(P × (V + E) log V) | O(V + E) | Graph build O(N² log N) |

Where:
- **P** = number of passengers
- **D** = number of drivers
- **V** = graph nodes = D + 2P
- **E** = graph edges = k × V (k = 4 nearest neighbors)

### Practical Trade-offs

```
Small fleet  (D < 30):  Greedy ≈ Heap ≈ Dijkstra (Greedy wins on simplicity)
Medium fleet (D ≈ 100): Heap outperforms Greedy by ~40%
Large fleet  (D > 200): Heap dominates; Dijkstra overhead becomes significant
Road-aware routing:     Dijkstra is the only correct choice
```

---

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Backend API

```bash
# From the project root
uvicorn api.main:app --reload --port 8000
```

The API will be live at: **http://127.0.0.1:8000**  
Swagger docs at: **http://127.0.0.1:8000/docs**  
Dashboard at: **http://127.0.0.1:8000/**

### 3. Open the Dashboard

Either visit `http://127.0.0.1:8000/` in your browser, or open `frontend/index.html` directly.

### 4. CLI Usage

```bash
# Run a greedy simulation
python main.py --algorithm greedy --drivers 20 --passengers 15

# Run a heap simulation
python main.py --algorithm heap --drivers 50 --passengers 40

# Run a Dijkstra simulation
python main.py --algorithm dijkstra --drivers 10 --passengers 8

# Compare all algorithms in a single run
python main.py --benchmark --drivers 30 --passengers 20

# Output raw JSON
python main.py --algorithm heap --json
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/simulate` | Run a simulation with given parameters |
| `GET` | `/api/drivers` | List drivers from last simulation |
| `GET` | `/api/passengers` | List passengers from last simulation |
| `GET` | `/api/metrics` | Performance metrics from last simulation |
| `GET` | `/api/trips` | Matched trip list from last simulation |
| `GET` | `/api/algorithms` | List available algorithms with complexity |
| `POST` | `/api/benchmark` | Run all 3 algorithms and compare |
| `GET` | `/health` | API health check |

### POST `/api/simulate` request body

```json
{
  "num_drivers":    20,
  "num_passengers": 15,
  "algorithm":      "greedy",
  "seed":           42,
  "lat_min":        28.40,
  "lat_max":        28.90,
  "lon_min":        77.00,
  "lon_max":        77.50
}
```

---

## Running Tests

```bash
# Run all tests with verbose output
pytest

# Run a specific test file
pytest tests/test_algorithms.py -v

# Run only greedy tests
pytest tests/test_algorithms.py -k "greedy"

# Show test coverage summary
pytest --tb=short
```

Expected output: **25+ tests passing** across models, algorithms, and dispatcher.

---

## Benchmarking

```bash
python benchmark/run_benchmark.py
```

Runs all 3 algorithms against 6 fleet-size scenarios (D=10 to D=500) and prints a formatted table:

```
══════════════════════════════════════════════════════════════════════════════════════════
  Smart Dispatch System — Full Algorithm Benchmark
══════════════════════════════════════════════════════════════════════════════════════════
Scenario               Algorithm                      Time (ms)    Matches  Match%  Avg Dist (km)
──────────────────────────────────────────────────────────────────────────────────────────
  D= 10, P=  8        Greedy Nearest Driver               0.241         8  100.0%        18.4721
  D= 10, P=  8        Heap Priority Queue                 0.193         8  100.0%        18.4721
  D= 10, P=  8        Dijkstra Graph Routing              8.102         8  100.0%        19.1034
...
```

Results are saved to `benchmark/results.json`.

---

## Design Patterns

### Strategy Pattern

The `Dispatcher` class accepts any `MatchingAlgorithm` subclass and delegates work to it:

```python
dispatcher = Dispatcher("heap")          # selects HeapMatcher
dispatcher.set_algorithm("dijkstra")     # hot-swaps to DijkstraMatcher
trips = dispatcher.dispatch(drivers, passengers)
```

This satisfies the **Open/Closed Principle** — new algorithms can be added by creating a new subclass of `MatchingAlgorithm` and registering it in `ALGORITHM_REGISTRY`.

### Separation of Concerns

| Layer | Responsibility |
|---|---|
| `models/` | Pure data — no business logic |
| `algorithms/` | Pure matching logic — no I/O |
| `system/` | Orchestration — no HTTP |
| `api/` | HTTP + serialization — no domain logic |
| `utils/` | Math + config — stateless helpers |

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Backend | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| Frontend | Vanilla HTML/CSS/JS |
| Charts | Chart.js 4 |
| Map | HTML Canvas API |
| Tests | pytest |
| Distance | Haversine formula |

---

## License

MIT — free to use, modify, and distribute.

---

*Built as a portfolio project demonstrating Design and Analysis of Algorithms (DAA), system design, and full-stack engineering.*

