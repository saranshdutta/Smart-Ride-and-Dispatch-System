import math


def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute Euclidean distance between two coordinate points.

    Time Complexity: O(1)
    Space Complexity: O(1)

    Suitable for small geographic areas where Earth's curvature is negligible.
    """
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute the great-circle distance between two points on Earth using the
    Haversine formula. Returns distance in kilometers.

    Time Complexity: O(1)
    Space Complexity: O(1)

    More accurate than Euclidean for real-world geographic coordinates.
    """
    R = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def manhattan_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute Manhattan (L1) distance — approximates grid-based city routing.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return abs(lat1 - lat2) + abs(lon1 - lon2)
