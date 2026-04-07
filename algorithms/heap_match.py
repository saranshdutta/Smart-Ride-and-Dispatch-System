import heapq
from typing import List

from algorithms.base import MatchingAlgorithm
from models.driver import Driver
from models.passenger import Passenger
from models.trip import Trip
from utils.distance import haversine_distance
from utils.metrics import MetricsCollector


class HeapMatcher(MatchingAlgorithm):
    """
    Priority Queue (Min-Heap) optimized matching algorithm.

    For each passenger, pre-builds a min-heap of all available drivers
    keyed by distance. The closest driver is extracted in O(log D) time,
    avoiding the O(D) linear scan of the greedy approach.

    Pre-processing:  O(D log D)  — heapify all available drivers
    Per passenger:   O(log D)     — heap extract minimum
    Total:           O(D log D + P log D)

    Time Complexity:  O((D + P) log D)
    Space Complexity: O(D)  — heap storage

    Trade-offs:
        + Faster per-match than greedy when D is large
        + Natural re-usability: rebuild heap per passenger as drivers are removed
        - Higher constant factor due to heap management
        - Slightly more complex implementation
    """

    @property
    def name(self) -> str:
        return "Heap Priority Queue"

    @property
    def time_complexity(self) -> str:
        return "O((D + P) log D)"

    @property
    def space_complexity(self) -> str:
        return "O(D)"

    def match(
        self,
        drivers: List[Driver],
        passengers: List[Passenger],
        metrics: MetricsCollector,
    ) -> List[Trip]:
        trips: List[Trip] = []
        available_ids = {d.id for d in drivers if d.available}
        driver_map = {d.id: d for d in drivers}

        for passenger in passengers:
            if not available_ids:
                break

            heap: List[tuple] = []
            for driver_id in available_ids:
                driver = driver_map[driver_id]
                dist = haversine_distance(
                    passenger.pickup_lat,
                    passenger.pickup_lon,
                    driver.latitude,
                    driver.longitude,
                )
                heapq.heappush(heap, (dist, driver_id))

            if not heap:
                continue

            best_distance, best_driver_id = heapq.heappop(heap)
            best_driver = driver_map[best_driver_id]

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
            available_ids.discard(best_driver_id)
            metrics.record_match(best_distance)
            trips.append(trip)

        return trips
