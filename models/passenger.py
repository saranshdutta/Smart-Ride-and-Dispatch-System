from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Passenger:
    """Represents a passenger requesting a ride."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    pickup_lat: float = 0.0
    pickup_lon: float = 0.0
    dropoff_lat: float = 0.0
    dropoff_lon: float = 0.0
    matched: bool = False
    assigned_driver_id: Optional[str] = None

    def __post_init__(self):
        if not self.name:
            self.name = f"Passenger-{self.id}"

    def assign_driver(self, driver_id: str):
        self.assigned_driver_id = driver_id
        self.matched = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "pickup_lat": self.pickup_lat,
            "pickup_lon": self.pickup_lon,
            "dropoff_lat": self.dropoff_lat,
            "dropoff_lon": self.dropoff_lon,
            "matched": self.matched,
            "assigned_driver_id": self.assigned_driver_id,
        }

    def __repr__(self) -> str:
        return (
            f"Passenger(id={self.id}, name={self.name}, "
            f"pickup=({self.pickup_lat:.4f}, {self.pickup_lon:.4f}), "
            f"matched={self.matched})"
        )
