import heapq
import math
from typing import Dict, List, Optional, Tuple

from algorithms.base import MatchingAlgorithm
from models.driver import Driver
from models.passenger import Passenger
from models.trip import Trip
from utils.distance import haversine_distance
from utils.metrics import MetricsCollector


def _build_road_graph(
    drivers: List[Driver],
    passengers: List[Passenger],
    k_nearest: int = 4,
) -> Tuple[List[tuple], Dict[str, int]]:
    """
    Build an undirected weighted graph from driver and passenger location nodes.

    Each node is a (lat, lon) location. Edges connect each node to its
    k_nearest neighbors based on Haversine distance, simulating a road network.

    Returns:
        adjacency: list of adjacency lists  adj[node_id] = [(neighbor_id, weight)]
        node_index: mapping from label string to node id
    """
    nodes: List[Tuple[float, float]] = []
    node_index: Dict[str, int] = {}

    for d in drivers:
        label = f"driver_{d.id}"
        if label not in node_index:
            node_index[label] = len(nodes)
            nodes.append((d.latitude, d.longitude))

    for p in passengers:
        for prefix, lat, lon in [
            (f"pickup_{p.id}", p.pickup_lat, p.pickup_lon),
            (f"dropoff_{p.id}", p.dropoff_lat, p.dropoff_lon),
        ]:
            if prefix not in node_index:
                node_index[prefix] = len(nodes)
                nodes.append((lat, lon))

    n = len(nodes)
    adjacency: List[List[Tuple[int, float]]] = [[] for _ in range(n)]

    for i in range(n):
        distances = []
        for j in range(n):
            if i == j:
                continue
            dist = haversine_distance(
                nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1]
            )
            distances.append((dist, j))
        distances.sort()
        for dist, j in distances[: min(k_nearest, len(distances))]:
            adjacency[i].append((j, dist))
            adjacency[j].append((i, dist))

    return adjacency, node_index, nodes


def _dijkstra(
    adjacency: List[List[Tuple[int, float]]],
    source: int,
    n: int,
) -> List[float]:
    """
    Classic Dijkstra's single-source shortest path algorithm.

    Time Complexity:  O((V + E) log V)  with binary heap (heapq)
    Space Complexity: O(V + E)

    Args:
        adjacency: adjacency list where adj[u] = [(v, weight), ...]
        source:    starting node index
        n:         total number of nodes

    Returns:
        dist: list of shortest distances from source to every node
    """
    INF = float("inf")
    dist = [INF] * n
    dist[source] = 0.0

    heap = [(0.0, source)]

    while heap:
        current_dist, u = heapq.heappop(heap)

        if current_dist > dist[u]:
            continue

        for v, weight in adjacency[u]:
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist


class DijkstraMatcher(MatchingAlgorithm):
    """
    Graph-based route-aware matching using Dijkstra's Algorithm.

    Constructs a simulated road-network graph from all driver and passenger
    locations. For each passenger, runs Dijkstra from their pickup node to
    find the shortest road-network distance to every available driver.
    The driver with minimum road-distance is selected.

    Graph construction: O(N² log N) — N = |drivers| + 2|passengers|
    Per-passenger Dijkstra: O((V + E) log V)
    Total:  O(P × (V + E) log V)

    Time Complexity:  O(P × (V + E) log V)
    Space Complexity: O(V + E)

    Trade-offs:
        + Accounts for real road-network routing paths
        + Produces a complete route (waypoints) for each trip
        - Significant pre-processing overhead for graph construction
        - Best suited when road topology differs significantly from straight-line
    """

    @property
    def name(self) -> str:
        return "Dijkstra Graph Routing"

    @property
    def time_complexity(self) -> str:
        return "O(P × (V + E) log V)"

    @property
    def space_complexity(self) -> str:
        return "O(V + E)"

    def match(
        self,
        drivers: List[Driver],
        passengers: List[Passenger],
        metrics: MetricsCollector,
    ) -> List[Trip]:
        trips: List[Trip] = []
        available_drivers = [d for d in drivers if d.available]

        if not available_drivers or not passengers:
            return trips

        adjacency, node_index, nodes = _build_road_graph(available_drivers, passengers)
        n = len(nodes)
        used_driver_ids: set = set()

        for passenger in passengers:
            pickup_label = f"pickup_{passenger.id}"
            dropoff_label = f"dropoff_{passenger.id}"

            if pickup_label not in node_index:
                continue

            pickup_node = node_index[pickup_label]
            dist_from_pickup = _dijkstra(adjacency, pickup_node, n)

            best_driver: Optional[Driver] = None
            best_road_dist = float("inf")

            for driver in available_drivers:
                if driver.id in used_driver_ids:
                    continue
                driver_label = f"driver_{driver.id}"
                driver_node = node_index.get(driver_label)
                if driver_node is None:
                    continue
                road_dist = dist_from_pickup[driver_node]
                if road_dist < best_road_dist:
                    best_road_dist = road_dist
                    best_driver = driver

            if best_driver is None:
                continue

            dropoff_node = node_index.get(dropoff_label)
            trip_dist = dist_from_pickup[dropoff_node] if dropoff_node is not None else 0.0

            route = [
                (best_driver.latitude, best_driver.longitude),
                (passenger.pickup_lat, passenger.pickup_lon),
                (passenger.dropoff_lat, passenger.dropoff_lon),
            ]

            trip = Trip(
                driver_id=best_driver.id,
                passenger_id=passenger.id,
                pickup_distance=best_road_dist,
                trip_distance=trip_dist,
                route=route,
                algorithm_used=self.name,
                status="completed",
            )

            best_driver.mark_busy()
            passenger.assign_driver(best_driver.id)
            used_driver_ids.add(best_driver.id)
            metrics.record_match(best_road_dist)
            trips.append(trip)

        return trips
