"""
Smart Ride Matching and Dispatch System — CLI Entry Point

Usage:
    python main.py --algorithm greedy --drivers 20 --passengers 15
    python main.py --algorithm heap --drivers 50 --passengers 40
    python main.py --algorithm dijkstra --drivers 10 --passengers 8
    python main.py --benchmark
"""

import argparse
import json
import sys

from system.simulator import Simulator
from system.dispatcher import Dispatcher
from utils.config import SimulationConfig


def print_separator(char: str = "─", width: int = 70):
    print(char * width)


def print_metrics(metrics: dict):
    print_separator()
    print(f"  Algorithm       : {metrics['algorithm']}")
    print(f"  Execution Time  : {metrics['execution_time_ms']:.3f} ms")
    print(f"  Total Matches   : {metrics['total_matches']} / {metrics['total_passengers']}")
    print(f"  Match Rate      : {metrics['match_rate_pct']}%")
    print(f"  Avg Distance    : {metrics['average_distance']:.4f} km")
    print(f"  Min Distance    : {metrics['min_distance']:.4f} km")
    print(f"  Max Distance    : {metrics['max_distance']:.4f} km")
    print_separator()


def run_simulation(args):
    config = SimulationConfig(
        num_drivers=args.drivers,
        num_passengers=args.passengers,
        algorithm=args.algorithm,
        seed=args.seed,
    )

    print(f"\n🚗  Smart Dispatch System — Running '{args.algorithm}' algorithm")
    print_separator("═")

    simulator = Simulator(config)
    result = simulator.run()

    print(f"\n📍 Drivers     : {args.drivers}")
    print(f"📍 Passengers  : {args.passengers}")

    print("\n📋 TRIP MATCHES:")
    for trip in result["trips"]:
        print(
            f"  ✅  Driver {trip['driver_id']} ➜ Passenger {trip['passenger_id']}  "
            f"| Pickup: {trip['pickup_distance']:.3f} km"
        )

    print("\n📊 PERFORMANCE METRICS:")
    print_metrics(result["metrics"])

    if args.json:
        print("\n🗄  JSON Output:")
        print(json.dumps(result, indent=2))


def run_benchmark(args):
    print("\n🏁  Smart Dispatch System — Algorithm Benchmark")
    print_separator("═")
    print(f"   Drivers: {args.drivers} | Passengers: {args.passengers} | Seed: {args.seed}\n")

    header = f"{'Algorithm':<30} {'Time (ms)':>12} {'Matches':>10} {'Match%':>8} {'Avg Dist':>12}"
    print(header)
    print_separator()

    for algo_key in ["greedy", "heap", "dijkstra"]:
        config = SimulationConfig(
            num_drivers=args.drivers,
            num_passengers=args.passengers,
            algorithm=algo_key,
            seed=args.seed,
        )
        simulator = Simulator(config)
        result = simulator.run()
        m = result["metrics"]
        print(
            f"{m['algorithm']:<30} "
            f"{m['execution_time_ms']:>11.3f} "
            f"{m['total_matches']:>10} "
            f"{m['match_rate_pct']:>7.1f}% "
            f"{m['average_distance']:>11.4f}"
        )

    print_separator()
    print("\n✅  Benchmark complete.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Smart Ride Matching and Dispatch System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--algorithm", choices=["greedy", "heap", "dijkstra"], default="greedy"
    )
    parser.add_argument("--drivers", type=int, default=20)
    parser.add_argument("--passengers", type=int, default=15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--benchmark", action="store_true", help="Compare all algorithms")
    parser.add_argument("--json", action="store_true", help="Output raw JSON result")

    args = parser.parse_args()

    if args.benchmark:
        run_benchmark(args)
    else:
        run_simulation(args)


if __name__ == "__main__":
    main()
