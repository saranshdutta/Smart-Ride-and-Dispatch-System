from abc import ABC, abstractmethod
from typing import List, Tuple

from models.driver import Driver
from models.passenger import Passenger
from models.trip import Trip
from utils.metrics import MetricsCollector


class MatchingAlgorithm(ABC):
    """
    Abstract Strategy base class for all matching algorithms.

    Implementing the Strategy Pattern allows the Dispatcher to swap
    algorithms at runtime without modifying client code.

    All subclasses must implement `match()` and expose `name` and
    `time_complexity` / `space_complexity` for benchmarking metadata.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def time_complexity(self) -> str:
        ...

    @property
    @abstractmethod
    def space_complexity(self) -> str:
        ...

    @abstractmethod
    def match(
        self,
        drivers: List[Driver],
        passengers: List[Passenger],
        metrics: MetricsCollector,
    ) -> List[Trip]:
        """
        Match available drivers to waiting passengers.

        Args:
            drivers: List of Driver objects (may include unavailable ones).
            passengers: List of Passenger objects waiting for a ride.
            metrics: MetricsCollector to record performance data.

        Returns:
            List of Trip objects representing successful matches.
        """
        ...
