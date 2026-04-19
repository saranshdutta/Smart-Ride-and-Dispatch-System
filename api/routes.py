from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from system.simulator import Simulator
from system.dispatcher import Dispatcher
from utils.config import SimulationConfig

router = APIRouter()


class SimulateRequest(BaseModel):
    num_drivers: int = Field(default=20, ge=1, le=500)
    num_passengers: int = Field(default=15, ge=1, le=500)
    algorithm: str = Field(default="greedy")
    lat_min: float = Field(default=28.40)
    lat_max: float = Field(default=28.90)
    lon_min: float = Field(default=77.00)
    lon_max: float = Field(default=77.50)
    seed: int = Field(default=42)


_last_result: dict = {}


@router.post("/simulate", tags=["Simulation"])
async def simulate(body: SimulateRequest):
    """
    Run a full ride-matching simulation with the specified algorithm and parameters.

    Returns matched trips, driver and passenger lists, and performance metrics.
    """
    global _last_result
    try:
        config = SimulationConfig(
            num_drivers=body.num_drivers,
            num_passengers=body.num_passengers,
            algorithm=body.algorithm,
            lat_min=body.lat_min,
            lat_max=body.lat_max,
            lon_min=body.lon_min,
            lon_max=body.lon_max,
            seed=body.seed,
        )
        config.validate()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    simulator = Simulator(config)
    result = simulator.run()
    _last_result = result
    return result


@router.get("/drivers", tags=["Data"])
async def get_drivers():
    """Return the driver list from the most recent simulation."""
    if not _last_result:
        raise HTTPException(status_code=404, detail="No simulation has been run yet.")
    return {"drivers": _last_result.get("drivers", [])}


@router.get("/passengers", tags=["Data"])
async def get_passengers():
    """Return the passenger list from the most recent simulation."""
    if not _last_result:
        raise HTTPException(status_code=404, detail="No simulation has been run yet.")
    return {"passengers": _last_result.get("passengers", [])}


@router.get("/metrics", tags=["Analytics"])
async def get_metrics():
    """Return performance metrics from the most recent simulation."""
    if not _last_result:
        raise HTTPException(status_code=404, detail="No simulation has been run yet.")
    return {"metrics": _last_result.get("metrics", {})}


@router.get("/trips", tags=["Data"])
async def get_trips():
    """Return matched trips from the most recent simulation."""
    if not _last_result:
        raise HTTPException(status_code=404, detail="No simulation has been run yet.")
    return {"trips": _last_result.get("trips", [])}


@router.get("/algorithms", tags=["System"])
async def list_algorithms():
    """List all available matching algorithms with their complexity details."""
    return {"algorithms": Dispatcher.available_algorithms()}


@router.post("/benchmark", tags=["Analytics"])
async def run_benchmark(
    num_drivers: int = Query(default=30, ge=5, le=200),
    num_passengers: int = Query(default=20, ge=5, le=200),
    seed: int = Query(default=99),
    lat_min: float = Query(default=28.40),
    lat_max: float = Query(default=28.90),
    lon_min: float = Query(default=77.00),
    lon_max: float = Query(default=77.50),
):
    """
    Run all three algorithms on identical input and return a side-by-side
    performance comparison.
    """
    results = []
    for algo_key in ["greedy", "heap", "dijkstra"]:
        config = SimulationConfig(
            num_drivers=num_drivers,
            num_passengers=num_passengers,
            algorithm=algo_key,
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            seed=seed,
        )
        simulator = Simulator(config)
        result = simulator.run()
        results.append(result["metrics"])

    return {"benchmark": results, "num_drivers": num_drivers, "num_passengers": num_passengers}
