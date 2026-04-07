from dataclasses import dataclass, field
from typing import List, Optional
import uuid


@dataclass
class Trip:
    """Represents a completed or in-progress ride trip."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    driver_id: str = ""
    passenger_id: str = ""
    pickup_distance: float = 0.0
    trip_distance: float = 0.0
    route: List[tuple] = field(default_factory=list)
    algorithm_used: str = ""
    status: str = "pending"

    def complete(self):
        self.status = "completed"

    @property
    def total_distance(self) -> float:
        return self.pickup_distance + self.trip_distance

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "driver_id": self.driver_id,
            "passenger_id": self.passenger_id,
            "pickup_distance": round(self.pickup_distance, 4),
            "trip_distance": round(self.trip_distance, 4),
            "total_distance": round(self.total_distance, 4),
            "route": self.route,
            "algorithm_used": self.algorithm_used,
            "status": self.status,
        }

    def __repr__(self) -> str:
        return (
            f"Trip(id={self.id}, driver={self.driver_id}, "
            f"passenger={self.passenger_id}, "
            f"pickup_dist={self.pickup_distance:.4f}, status={self.status})"
        )
