from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """
    Configurable parameters for the ride-hailing simulation.

    These values control the size and geographic scope of the simulation
    and can be overridden via the API or CLI.
    """

    num_drivers: int = 20
    num_passengers: int = 15
    grid_size: float = 10.0
    lat_min: float = 28.40
    lat_max: float = 28.90
    lon_min: float = 77.00
    lon_max: float = 77.50
    algorithm: str = "greedy"
    seed: int = 42

    VALID_ALGORITHMS = {"greedy", "heap", "dijkstra"}

    def validate(self):
        if self.algorithm not in self.VALID_ALGORITHMS:
            raise ValueError(
                f"Unknown algorithm '{self.algorithm}'. "
                f"Valid options: {self.VALID_ALGORITHMS}"
            )
        if self.num_drivers < 1 or self.num_passengers < 1:
            raise ValueError("Must have at least 1 driver and 1 passenger.")
        if self.lat_min >= self.lat_max or self.lon_min >= self.lon_max:
            raise ValueError("Invalid geographic bounds.")

    def to_dict(self) -> dict:
        return {
            "num_drivers": self.num_drivers,
            "num_passengers": self.num_passengers,
            "algorithm": self.algorithm,
            "lat_range": [self.lat_min, self.lat_max],
            "lon_range": [self.lon_min, self.lon_max],
            "seed": self.seed,
        }
