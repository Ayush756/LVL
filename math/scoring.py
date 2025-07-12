# scoring.py (part 1 of 3)
import numpy as np
from normalization import min_max_scale

def demographic_fit_score(populations, incomes):
    """
    Compute a demographic fit score for each location given lists of 
    population and average income. Both lists must be same length.
    Score = (normalized_population + normalized_income) / 2.
    Higher score means more people and higher income (better target market).
    """
    pop_arr = np.array(populations, dtype=float)
    inc_arr = np.array(incomes, dtype=float)
    # Normalize to [0,1]
    pop_norm = min_max_scale(pop_arr)
    inc_norm = min_max_scale(inc_arr)
    # Combine by averaging
    return (pop_norm + inc_norm) / 2

# # scoring.py (part 2 of 3)
# def competition_score(competitor_counts):
#     """
#     Compute a competition score from a list of competitor counts.
#     We min-max normalize the counts (more competitors => higher normalized value),
#     then invert: score = 1 - normalized_competitors.
#     So fewer competitors -> score close to 1, more -> closer to 0.
#     """
#     comp_arr = np.array(competitor_counts, dtype=float)
#     # Normalize to [0,1]
#     comp_norm = min_max_scale(comp_arr)
#     # Invert: fewer competitors -> higher score
#     return 1 - comp_norm

# scoring.py (part 3 of 3)
def poi_amenity_score(amenity_counts):
    """
    Compute a POI/amenity score given a list of counts of nearby facilities.
    We normalize the counts so that locations with more amenities score higher.
    """
    poi_arr = np.array(amenity_counts, dtype=float)
    # Normalize to [0,1] (more amenities => higher normalized value)
    return min_max_scale(poi_arr)

# scoring.py (continued)
def accessibility_score(footfalls, connectivity):
    """
    Compute an accessibility score from foot traffic and connectivity data.
    Both inputs are lists (same length). We normalize each and take the average:
    score = (normalized_footfall + normalized_connectivity) / 2.
    """
    foot_arr = np.array(footfalls, dtype=float)
    conn_arr = np.array(connectivity, dtype=float)
    foot_norm = min_max_scale(foot_arr)
    conn_norm = min_max_scale(conn_arr)
    return (foot_norm + conn_norm) / 2

def normalize_distance(distances):
    d = np.array(distances, dtype=float)
    d_min = d.min()
    d_max = d.max()
    if d_max == d_min:
        return np.ones_like(d)  # if all distances same, assign 1
    return (d_max - d) / (d_max - d_min)  # closer = higher score


#affordability = revenue / (revenue + rent)

# # scoring.py (continued)
def affordability_score(rents, revenues):
    """
    Compute an affordability index from lists of rents and expected revenues.
    We compute revenue/(revenue+rent) for each location.
    Higher means revenue >> rent (good); lower means rent is high relative to revenue.
    """
    rent_arr = np.array(rents, dtype=float)
    rev_arr = np.array(revenues, dtype=float)
    # Avoid division by zero: if revenue+rent is zero, set score to 0
    total = rev_arr + rent_arr
    with np.errstate(divide='ignore', invalid='ignore'):
        idx = np.where(total != 0, rev_arr / total, 0)
    # Ensure values are between 0 and 1
    idx = np.clip(idx, 0, 1)
    return idx

def weighted_score(factor_scores, weights):
    """
    Compute final weighted score given list of factor scores (floats)
    and corresponding list of weights. Both lengths must match.
    Returns a single float (weighted sum).
    """
    scores = np.array(factor_scores, dtype=float)
    w = np.array(weights, dtype=float)
    if scores.shape[0] != w.shape[0]:
        raise ValueError("Number of factors and weights must match")
    return np.dot(scores, w)