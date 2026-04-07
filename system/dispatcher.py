from typing import List, Optional

from algorithms.base import MatchingAlgorithm
from algorithms.greedy import GreedyMatcher
from algorithms.heap_match import HeapMatcher
from algorithms.dijkstra import DijkstraMatcher
from models.driver import Driver
from models.passenger import Passenger
from models.trip import Trip
from utils.metrics import MetricsCollector


ALGORITHM_REGISTRY: dict = {
    "greedy": GreedyMatcher,
    "heap": HeapMatcher,
    "dijkstra": DijkstraMatcher,
}


class Dispatcher:
    """
    Strategy-pattern dispatcher that delegates matching to a pluggable algorithm.

    The algorithm can be swapped at runtime without modifying any client code,
    fully demonstrating the Open/Closed Principle.

    Usage:
        dispatcher = Dispatcher("heap")
        trips = dispatcher.dispatch(drivers, passengers)
        print(dispatcher.metrics)
    """

    def __init__(self, algorithm: str = "greedy"):
        self._algorithm_key = algorithm
        self._strategy: MatchingAlgorithm = self._resolve(algorithm)
        self._metrics: Optional[MetricsCollector] = None
        self._last_trips: List[Trip] = []

    @staticmethod
    def _resolve(algorithm: str) -> MatchingAlgorithm:
        if algorithm not in ALGORITHM_REGISTRY:
            raise ValueError(
                f"Algorithm '{algorithm}' is not registered. "
                f"Available: {list(ALGORITHM_REGISTRY.keys())}"
            )
        return ALGORITHM_REGISTRY[algorithm]()

    def set_algorithm(self, algorithm: str):
        """Hot-swap the matching strategy at runtime."""
        self._algorithm_key = algorithm
        self._strategy = self._resolve(algorithm)

    @property
    def algorithm_name(self) -> str:
        return self._strategy.name

    @property
    def metrics(self) -> Optional[MetricsCollector]:
        return self._metrics

    @property
    def last_trips(self) -> List[Trip]:
        return self._last_trips

    def dispatch(
        self,
        drivers: List[Driver],
        passengers: List[Passenger],
    ) -> List[Trip]:
        """
        Run the selected algorithm against the given fleet and passengers.

        Resets driver/passenger state before each call so the dispatcher
        can be reused across multiple simulation runs cleanly.

        Returns:
            List of completed Trip objects.
        """
        metrics = MetricsCollector(
            algorithm_name=self._strategy.name,
            total_drivers=len(drivers),
            total_passengers=len(passengers),
        )

        metrics.start()
        trips = self._strategy.match(drivers, passengers, metrics)
        metrics.stop()

        self._metrics = metrics
        self._last_trips = trips
        return trips

    def algorithm_info(self) -> dict:
        return {
            "key": self._algorithm_key,
            "name": self._strategy.name,
            "time_complexity": self._strategy.time_complexity,
            "space_complexity": self._strategy.space_complexity,
        }

    @staticmethod
    def available_algorithms() -> List[dict]:
        strategies = {
            "greedy": GreedyMatcher(),
            "heap": HeapMatcher(),
            "dijkstra": DijkstraMatcher(),
        }
        return [
            {
                "key": k,
                "name": v.name,
                "time_complexity": v.time_complexity,
                "space_complexity": v.space_complexity,
            }
            for k, v in strategies.items()
        ]
