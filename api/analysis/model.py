import numpy as np

# Gravity Model
def gravity_model(populations, distances, attractiveness=None, beta=3):
    """
    Computes the gravity score for each location.
    G_i = (P_i * A_i) / D_i^β
    - populations: list of populations at each site
    - distances: list of distances (lower = better)
    - attractiveness: optional list of attractiveness (e.g. revenue potential). If None, set to 1
    - beta: distance decay factor (default = 2)
    Returns: array of gravity scores
    """
    P = np.array(populations, dtype=float)
    D = np.array(distances, dtype=float)
    if attractiveness is None:
        A = np.ones_like(P)
    else:
        A = np.array(attractiveness, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        gravity_scores = (P * A) / (D ** beta)
    gravity_scores[np.isnan(gravity_scores)] = 0
    return gravity_scores


# Huff Model
def huff_model(attractiveness, distances, beta=2):
    """
    Computes the Huff probability for each location:
    H_i = (A_i / D_i^β) / Σ_j (A_j / D_j^β)
    - attractiveness: list of site attractiveness scores
    - distances: list of distances to each site
    - beta: distance decay parameter (default = 2)
    Returns: array of probabilities that a consumer selects each site
    """
    A = np.array(attractiveness, dtype=float)
    D = np.array(distances, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        numerator = A / (D ** beta)
        numerator[np.isnan(numerator)] = 0
        denom = np.sum(numerator)
        if denom == 0:
            return np.zeros_like(numerator)
        probabilities = numerator / denom
    return probabilities

"""
# Sample data for 3 locations
populations = [12000, 8000, 15000]
distances = [0.5, 1.2, 0.7]  # distance to user or central point (km)
revenues = [3000, 1500, 5000]  # used as attractiveness

gravity_scores = gravity_model(populations, distances, revenues)
huff_probabilities = huff_model(revenues, distances)

gravity_scores, huff_probabilities

"""