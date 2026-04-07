from typing import List

from algorithms.base import MatchingAlgorithm
from models.driver import Driver
from models.passenger import Passenger
from models.trip import Trip
from utils.distance import haversine_distance
from utils.metrics import MetricsCollector


class GreedyMatcher(MatchingAlgorithm):
    """
    Greedy nearest-driver matching algorithm.

    For each passenger (in order of arrival), scans all available drivers
    and picks the one with the smallest Haversine distance.

    Time Complexity:  O(P × D) — P passengers, D drivers
    Space Complexity: O(1) auxiliary (beyond input/output storage)

    Trade-offs:
        + Simple, low overhead, zero pre-processing
        - Does not globally optimize total distance
        - Greedy choices may leave distant drivers unmatched
    """

    @property
    def name(self) -> str:
        return "Greedy Nearest Driver"

    @property
    def time_complexity(self) -> str:
        return "O(P × D)"

    @property
    def space_complexity(self) -> str:
        return "O(1)"

    def match(
        self,
        drivers: List[Driver],
        passengers: List[Passenger],
        metrics: MetricsCollector,
    ) -> List[Trip]:
        trips: List[Trip] = []
        available = [d for d in drivers if d.available]

        for passenger in passengers:
            if not available:
                break

            best_driver = None
            best_distance = float("inf")

            for driver in available:
                dist = haversine_distance(
                    passenger.pickup_lat,
                    passenger.pickup_lon,
                    driver.latitude,
                    driver.longitude,
                )
                if dist < best_distance:
                    best_distance = dist
                    best_driver = driver

            if best_driver is not None:
                trip_distance = haversine_distance(
                    passenger.pickup_lat,
                    passenger.pickup_lon,
                    passenger.dropoff_lat,
                    passenger.dropoff_lon,
                )

                trip = Trip(
                    driver_id=best_driver.id,
                    passenger_id=passenger.id,
                    pickup_distance=best_distance,
                    trip_distance=trip_distance,
                    route=[
                        (best_driver.latitude, best_driver.longitude),
                        (passenger.pickup_lat, passenger.pickup_lon),
                        (passenger.dropoff_lat, passenger.dropoff_lon),
                    ],
                    algorithm_used=self.name,
                    status="completed",
                )

                best_driver.mark_busy()
                passenger.assign_driver(best_driver.id)
                available.remove(best_driver)
                metrics.record_match(best_distance)
                trips.append(trip)

        return trips
