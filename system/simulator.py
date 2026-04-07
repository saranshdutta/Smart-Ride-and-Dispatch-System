import random
from typing import Dict, List, Optional

from models.driver import Driver
from models.passenger import Passenger
from models.trip import Trip
from system.dispatcher import Dispatcher
from utils.config import SimulationConfig
from utils.metrics import MetricsCollector


class Simulator:
    """
    Orchestrates a full ride-matching simulation run.

    Generates random driver and passenger populations within the configured
    geographic bounds, then delegates to the Dispatcher for matching.

    Supports seeded randomness for reproducible benchmarks.
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.config.validate()
        self._rng = random.Random(self.config.seed)
        self._drivers: List[Driver] = []
        self._passengers: List[Passenger] = []
        self._trips: List[Trip] = []
        self._metrics: Optional[MetricsCollector] = None

    def _random_lat(self) -> float:
        return self._rng.uniform(self.config.lat_min, self.config.lat_max)

    def _random_lon(self) -> float:
        return self._rng.uniform(self.config.lon_min, self.config.lon_max)

    def generate_drivers(self) -> List[Driver]:
        """Generate a fleet of drivers at random locations."""
        drivers = []
        for i in range(self.config.num_drivers):
            driver = Driver(
                latitude=self._random_lat(),
                longitude=self._random_lon(),
                available=True,
                rating=round(self._rng.uniform(3.5, 5.0), 2),
            )
            drivers.append(driver)
        self._drivers = drivers
        return drivers

    def generate_passengers(self) -> List[Passenger]:
        """Generate passengers with random pickup and dropoff locations."""
        passengers = []
        for i in range(self.config.num_passengers):
            passenger = Passenger(
                pickup_lat=self._random_lat(),
                pickup_lon=self._random_lon(),
                dropoff_lat=self._random_lat(),
                dropoff_lon=self._random_lon(),
            )
            passengers.append(passenger)
        self._passengers = passengers
        return passengers

    def run(self) -> Dict:
        """
        Execute a complete simulation:
          1. Generate drivers and passengers
          2. Dispatch using configured algorithm
          3. Collect and return metrics + trip data

        Returns:
            A structured result dict with trips, metrics, drivers, passengers.
        """
        drivers = self.generate_drivers()
        passengers = self.generate_passengers()

        dispatcher = Dispatcher(algorithm=self.config.algorithm)
        trips = dispatcher.dispatch(drivers, passengers)

        self._trips = trips
        self._metrics = dispatcher.metrics

        return {
            "algorithm": dispatcher.algorithm_info(),
            "trips": [t.to_dict() for t in trips],
            "metrics": self._metrics.to_dict() if self._metrics else {},
            "drivers": [d.to_dict() for d in drivers],
            "passengers": [p.to_dict() for p in passengers],
            "config": self.config.to_dict(),
        }

    @property
    def drivers(self) -> List[Driver]:
        return self._drivers

    @property
    def passengers(self) -> List[Passenger]:
        return self._passengers

    @property
    def trips(self) -> List[Trip]:
        return self._trips

    @property
    def metrics(self) -> Optional[MetricsCollector]:
        return self._metrics
