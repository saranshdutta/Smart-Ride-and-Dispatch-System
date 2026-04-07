"""
Benchmark: Compare Greedy, Heap, and Dijkstra across increasing fleet sizes.

Run:
    python benchmark/run_benchmark.py

Output:
    Console table + results saved to benchmark/results.json
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from system.simulator import Simulator
from utils.config import SimulationConfig

SCENARIOS = [
    {"num_drivers": 10, "num_passengers": 8},
    {"num_drivers": 25, "num_passengers": 20},
    {"num_drivers": 50, "num_passengers": 40},
    {"num_drivers": 100, "num_passengers": 80},
    {"num_drivers": 200, "num_passengers": 150},
    {"num_drivers": 500, "num_passengers": 400},
]

ALGORITHMS = ["greedy", "heap", "dijkstra"]
SEED = 2024


def run_benchmark():
    print("\n" + "=" * 90)
    print("  Smart Dispatch System — Full Algorithm Benchmark")
    print("=" * 90)

    header = (
        f"{'Scenario':<22} {'Algorithm':<28} "
        f"{'Time (ms)':>10} {'Matches':>9} {'Match%':>8} {'Avg Dist (km)':>14}"
    )
    print(header)
    print("-" * 90)

    all_results = []

    for scenario in SCENARIOS:
        d, p = scenario["num_drivers"], scenario["num_passengers"]
        scenario_label = f"D={d:>3}, P={p:>3}"

        for algo in ALGORITHMS:
            config = SimulationConfig(
                num_drivers=d,
                num_passengers=p,
                algorithm=algo,
                seed=SEED,
            )
            simulator = Simulator(config)
            result = simulator.run()
            m = result["metrics"]

            row = {
                "scenario": scenario_label,
                "num_drivers": d,
                "num_passengers": p,
                **m,
            }
            all_results.append(row)

            print(
                f"  {scenario_label:<20} {m['algorithm']:<28} "
                f"{m['execution_time_ms']:>9.3f} "
                f"{m['total_matches']:>9} "
                f"{m['match_rate_pct']:>7.1f}% "
                f"{m['average_distance']:>13.4f}"
            )

        print("-" * 90)

    output_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅  Results saved to: {output_path}")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    run_benchmark()
