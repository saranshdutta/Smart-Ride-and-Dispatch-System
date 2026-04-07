import time
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class MetricsCollector:
    """
    Collects and aggregates performance metrics for a simulation run.

    Tracks execution time, match counts, and distance statistics to enable
    algorithm comparison across multiple runs.
    """

    algorithm_name: str = ""
    total_matches: int = 0
    total_passengers: int = 0
    total_drivers: int = 0
    distances: List[float] = field(default_factory=list)
    _start_time: float = field(default=0.0, repr=False, compare=False)
    _end_time: float = field(default=0.0, repr=False, compare=False)

    def start(self):
        self._start_time = time.perf_counter()

    def stop(self):
        self._end_time = time.perf_counter()

    def record_match(self, distance: float):
        self.total_matches += 1
        self.distances.append(distance)

    @property
    def elapsed_seconds(self) -> float:
        if self._end_time and self._start_time:
            return self._end_time - self._start_time
        return 0.0

    @property
    def match_rate(self) -> float:
        if self.total_passengers == 0:
            return 0.0
        return round(self.total_matches / self.total_passengers * 100, 2)

    @property
    def average_distance(self) -> float:
        if not self.distances:
            return 0.0
        return round(sum(self.distances) / len(self.distances), 4)

    @property
    def min_distance(self) -> float:
        return round(min(self.distances), 4) if self.distances else 0.0

    @property
    def max_distance(self) -> float:
        return round(max(self.distances), 4) if self.distances else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm_name,
            "execution_time_ms": round(self.elapsed_seconds * 1000, 3),
            "total_matches": self.total_matches,
            "total_passengers": self.total_passengers,
            "total_drivers": self.total_drivers,
            "match_rate_pct": self.match_rate,
            "average_distance": self.average_distance,
            "min_distance": self.min_distance,
            "max_distance": self.max_distance,
        }

    def __repr__(self) -> str:
        return (
            f"Metrics(algo={self.algorithm_name}, "
            f"time={self.elapsed_seconds * 1000:.3f}ms, "
            f"matches={self.total_matches}/{self.total_passengers}, "
            f"avg_dist={self.average_distance})"
        )
