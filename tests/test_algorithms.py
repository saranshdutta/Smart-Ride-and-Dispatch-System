import pytest
from models.driver import Driver
from models.passenger import Passenger
from algorithms.greedy import GreedyMatcher
from algorithms.heap_match import HeapMatcher
from algorithms.dijkstra import DijkstraMatcher
from utils.metrics import MetricsCollector


def make_drivers(coords):
    return [Driver(latitude=lat, longitude=lon) for lat, lon in coords]


def make_passengers(pickups, dropoffs=None):
    if dropoffs is None:
        dropoffs = [(lat + 0.05, lon + 0.05) for lat, lon in pickups]
    return [
        Passenger(
            pickup_lat=lat, pickup_lon=lon,
            dropoff_lat=dlat, dropoff_lon=dlon
        )
        for (lat, lon), (dlat, dlon) in zip(pickups, dropoffs)
    ]


DRIVER_COORDS = [(28.5, 77.1), (28.6, 77.2), (28.7, 77.3)]
PASSENGER_COORDS = [(28.51, 77.11), (28.61, 77.21)]


@pytest.mark.parametrize("MatcherClass", [GreedyMatcher, HeapMatcher, DijkstraMatcher])
class TestAllAlgorithms:
    def test_matches_within_available_drivers(self, MatcherClass):
        drivers = make_drivers(DRIVER_COORDS)
        passengers = make_passengers(PASSENGER_COORDS)
        metrics = MetricsCollector()
        matcher = MatcherClass()
        trips = matcher.match(drivers, passengers, metrics)
        assert len(trips) == len(passengers)

    def test_no_double_assignment(self, MatcherClass):
        drivers = make_drivers(DRIVER_COORDS)
        passengers = make_passengers(PASSENGER_COORDS)
        metrics = MetricsCollector()
        matcher = MatcherClass()
        trips = matcher.match(drivers, passengers, metrics)
        driver_ids_used = [t.driver_id for t in trips]
        assert len(driver_ids_used) == len(set(driver_ids_used))

    def test_returns_empty_when_no_drivers(self, MatcherClass):
        passengers = make_passengers(PASSENGER_COORDS)
        metrics = MetricsCollector()
        matcher = MatcherClass()
        trips = matcher.match([], passengers, metrics)
        assert trips == []

    def test_returns_empty_when_no_passengers(self, MatcherClass):
        drivers = make_drivers(DRIVER_COORDS)
        metrics = MetricsCollector()
        matcher = MatcherClass()
        trips = matcher.match(drivers, [], metrics)
        assert trips == []

    def test_partial_match_when_fewer_drivers(self, MatcherClass):
        drivers = make_drivers([(28.5, 77.1)])
        passengers = make_passengers(PASSENGER_COORDS)
        metrics = MetricsCollector()
        matcher = MatcherClass()
        trips = matcher.match(drivers, passengers, metrics)
        assert len(trips) == 1

    def test_all_trips_have_valid_structure(self, MatcherClass):
        drivers = make_drivers(DRIVER_COORDS)
        passengers = make_passengers(PASSENGER_COORDS)
        metrics = MetricsCollector()
        matcher = MatcherClass()
        trips = matcher.match(drivers, passengers, metrics)
        for trip in trips:
            assert trip.driver_id != ""
            assert trip.passenger_id != ""
            assert trip.pickup_distance >= 0
            assert trip.status == "completed"

    def test_metrics_recorded(self, MatcherClass):
        drivers = make_drivers(DRIVER_COORDS)
        passengers = make_passengers(PASSENGER_COORDS)
        metrics = MetricsCollector()
        matcher = MatcherClass()
        trips = matcher.match(drivers, passengers, metrics)
        assert metrics.total_matches == len(trips)
        assert len(metrics.distances) == len(trips)

    def test_algorithm_name_not_empty(self, MatcherClass):
        matcher = MatcherClass()
        assert len(matcher.name) > 0
        assert len(matcher.time_complexity) > 0
        assert len(matcher.space_complexity) > 0


class TestGreedySpecific:
    def test_picks_nearest_driver(self):
        drivers = [
            Driver(latitude=28.50, longitude=77.10),  # very close
            Driver(latitude=29.00, longitude=78.00),  # far away
        ]
        passengers = [Passenger(pickup_lat=28.51, pickup_lon=77.11,
                                dropoff_lat=28.60, dropoff_lon=77.20)]
        metrics = MetricsCollector()
        trips = GreedyMatcher().match(drivers, passengers, metrics)
        assert trips[0].driver_id == drivers[0].id
