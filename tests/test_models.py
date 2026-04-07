import pytest
from models.driver import Driver
from models.passenger import Passenger
from models.trip import Trip


class TestDriver:
    def test_default_name_generated(self):
        d = Driver()
        assert d.name.startswith("Driver-")

    def test_mark_busy_and_available(self):
        d = Driver()
        assert d.available is True
        d.mark_busy()
        assert d.available is False
        d.mark_available()
        assert d.available is True

    def test_complete_trip_increments_count(self):
        d = Driver(completed_trips=0, rating=4.0)
        d.complete_trip(rating=5.0)
        assert d.completed_trips == 1
        assert d.available is True
        assert 4.0 <= d.rating <= 5.0

    def test_to_dict_keys(self):
        d = Driver(latitude=28.5, longitude=77.1)
        data = d.to_dict()
        for key in ["id", "name", "latitude", "longitude", "available", "rating", "completed_trips"]:
            assert key in data

    def test_unique_ids(self):
        ids = {Driver().id for _ in range(100)}
        assert len(ids) == 100


class TestPassenger:
    def test_default_name_generated(self):
        p = Passenger()
        assert p.name.startswith("Passenger-")

    def test_assign_driver(self):
        p = Passenger()
        assert p.matched is False
        p.assign_driver("drv-xyz")
        assert p.matched is True
        assert p.assigned_driver_id == "drv-xyz"

    def test_to_dict_keys(self):
        p = Passenger(pickup_lat=28.6, pickup_lon=77.2, dropoff_lat=28.7, dropoff_lon=77.3)
        data = p.to_dict()
        for key in ["id", "name", "pickup_lat", "pickup_lon", "dropoff_lat", "dropoff_lon", "matched"]:
            assert key in data


class TestTrip:
    def test_total_distance(self):
        t = Trip(pickup_distance=2.5, trip_distance=5.0)
        assert t.total_distance == pytest.approx(7.5)

    def test_complete_changes_status(self):
        t = Trip()
        assert t.status == "pending"
        t.complete()
        assert t.status == "completed"

    def test_to_dict_structure(self):
        t = Trip(driver_id="d1", passenger_id="p1", pickup_distance=1.0, trip_distance=3.0)
        data = t.to_dict()
        assert data["driver_id"] == "d1"
        assert data["passenger_id"] == "p1"
        assert data["total_distance"] == pytest.approx(4.0)
