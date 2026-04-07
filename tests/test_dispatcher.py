import pytest
from models.driver import Driver
from models.passenger import Passenger
from system.dispatcher import Dispatcher
from system.simulator import Simulator
from utils.config import SimulationConfig


class TestDispatcher:
    def test_default_algorithm_is_greedy(self):
        d = Dispatcher()
        assert "Greedy" in d.algorithm_name

    def test_set_algorithm_switches_strategy(self):
        d = Dispatcher("greedy")
        d.set_algorithm("heap")
        assert "Heap" in d.algorithm_name

    def test_invalid_algorithm_raises(self):
        with pytest.raises(ValueError):
            Dispatcher("unknown_algo")

    def test_dispatch_returns_trips(self):
        d = Dispatcher("greedy")
        drivers = [Driver(latitude=28.5, longitude=77.1) for _ in range(5)]
        passengers = [
            Passenger(pickup_lat=28.51, pickup_lon=77.11,
                      dropoff_lat=28.6, dropoff_lon=77.2)
            for _ in range(3)
        ]
        trips = d.dispatch(drivers, passengers)
        assert len(trips) == 3

    def test_metrics_populated_after_dispatch(self):
        d = Dispatcher("heap")
        drivers = [Driver(latitude=28.5, longitude=77.1) for _ in range(3)]
        passengers = [
            Passenger(pickup_lat=28.6, pickup_lon=77.2,
                      dropoff_lat=28.7, dropoff_lon=77.3)
        ]
        d.dispatch(drivers, passengers)
        assert d.metrics is not None
        assert d.metrics.total_matches == 1

    def test_available_algorithms_returns_three(self):
        algos = Dispatcher.available_algorithms()
        assert len(algos) == 3
        keys = {a["key"] for a in algos}
        assert keys == {"greedy", "heap", "dijkstra"}

    def test_algorithm_info_has_complexity(self):
        d = Dispatcher("dijkstra")
        info = d.algorithm_info()
        assert "time_complexity" in info
        assert "space_complexity" in info


class TestSimulator:
    def test_generates_correct_counts(self):
        config = SimulationConfig(num_drivers=10, num_passengers=7, seed=1)
        sim = Simulator(config)
        drivers = sim.generate_drivers()
        passengers = sim.generate_passengers()
        assert len(drivers) == 10
        assert len(passengers) == 7

    def test_run_returns_required_keys(self):
        config = SimulationConfig(num_drivers=5, num_passengers=3, seed=7)
        sim = Simulator(config)
        result = sim.run()
        for key in ["algorithm", "trips", "metrics", "drivers", "passengers", "config"]:
            assert key in result

    def test_seeded_runs_are_deterministic(self):
        config1 = SimulationConfig(num_drivers=10, num_passengers=8, seed=42)
        config2 = SimulationConfig(num_drivers=10, num_passengers=8, seed=42)
        r1 = Simulator(config1).run()
        r2 = Simulator(config2).run()
        assert r1["metrics"]["total_matches"] == r2["metrics"]["total_matches"]
        assert r1["metrics"]["average_distance"] == r2["metrics"]["average_distance"]

    def test_invalid_config_raises(self):
        config = SimulationConfig(num_drivers=0, num_passengers=5)
        with pytest.raises(ValueError):
            config.validate()

    def test_all_algorithms_complete(self):
        for algo in ["greedy", "heap", "dijkstra"]:
            config = SimulationConfig(num_drivers=8, num_passengers=5, algorithm=algo, seed=10)
            result = Simulator(config).run()
            assert result["metrics"]["total_matches"] >= 0
