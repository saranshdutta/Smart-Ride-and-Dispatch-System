from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Driver:
    """Represents a driver in the ride-hailing system."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    available: bool = True
    rating: float = 4.5
    completed_trips: int = 0

    def __post_init__(self):
        if not self.name:
            self.name = f"Driver-{self.id}"

    def mark_busy(self):
        self.available = False

    def mark_available(self):
        self.available = True

    def complete_trip(self, rating: float = 4.5):
        self.completed_trips += 1
        self.rating = round((self.rating + rating) / 2, 2)
        self.mark_available()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "available": self.available,
            "rating": self.rating,
            "completed_trips": self.completed_trips,
        }

    def __repr__(self) -> str:
        return (
            f"Driver(id={self.id}, name={self.name}, "
            f"loc=({self.latitude:.4f}, {self.longitude:.4f}), "
            f"available={self.available}, rating={self.rating})"
        )
