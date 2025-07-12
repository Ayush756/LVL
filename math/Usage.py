import numpy as np
import random

from scoring import (
    demographic_fit_score,
    competition_score,
    poi_amenity_score,
    accessibility_score,
    affordability_score,
    weighted_score
)
from model import gravity_model, huff_model
from normalization import min_max_scale
from ahp import ahp_weights  # <-- AHP is now used

# === 1. Candidate location data ===
population       = [12000]
income           = [500]
competitors      = [random.randint(3, 10)]
amenities        = [20]
footfall         = [1000]
connectivity     = [5]
rent             = [1000]
revenue          = [3000]
attractiveness   = revenue
distance         = [0.8]

# === 2. Competitor data ===
num_competitors = 5
competitor_attractiveness = [random.randint(1500, 4000) for _ in range(num_competitors)]
competitor_distances = [round(random.uniform(0.5, 3.0), 2) for _ in range(num_competitors)]

# === 3. Combine candidate + competitors ===
all_attractiveness = attractiveness + competitor_attractiveness
all_distances = distance + competitor_distances
all_populations = population * len(all_attractiveness)

# === 4. Compute Huff and Gravity
huff_scores = huff_model(all_attractiveness, all_distances, beta=2)
S_huff = [huff_scores[0]]  # Candidate only

G_raw = gravity_model(all_populations, all_distances, all_attractiveness, beta=2)
S_grav = [min_max_scale(G_raw)[0]]

# === 5. Compute other scores
S_dem  = demographic_fit_score(population, income)
S_comp = competition_score(competitors)
S_poi  = poi_amenity_score(amenities)
S_acc  = accessibility_score(footfall, connectivity)
S_aff  = affordability_score(rent, revenue)
S_dist = [1 - min_max_scale(all_distances)[0]]  # closer = higher

# === 6. Stack factor scores
factor_matrix = np.vstack([
    S_dem, S_comp, S_poi, S_acc, S_aff, S_huff, S_grav, S_dist
])

criteria_names = [
    "demographic", "competition", "poi_amenity", "accessibility",
    "affordability", "huff_model", "gravity_model", "distance"
]

# === 7. AHP pairwise comparison matrix (customize if needed)
pairwise_matrix = [
    [1,     2,     3,    3,     4,     3,    3,    5],
    [0.5,   1,     2,    2,     3,     2,    2,    4],
    [0.33,  0.5,   1,    1,     2,     1,    1,    2],
    [0.33,  0.5,   1,    1,     2,     1,    1,    2],
    [0.25,  0.33,  0.5,  0.5,   1,     1,    0.5,  2],
    [0.33,  0.5,   1,    1,     1,     1,    1,    2],
    [0.33,  0.5,   1,    1,     2,     1,    1,    2],
    [0.2,   0.25,  0.5,  0.5,   0.5,   0.5,  0.5,  1]
]
weights = ahp_weights(pairwise_matrix)

# === 8. Final score
final_score = weighted_score(factor_matrix, weights)[0]

# === 9. Output
print("\n--- Candidate Location ---")
print(f"Population        : {population[0]}")
print(f"Income            : ${income[0]}")
print(f"Competitors       : {competitors[0]}")
print(f"Amenities         : {amenities[0]}")
print(f"Footfall          : {footfall[0]}")
print(f"Connectivity      : {connectivity[0]}")
print(f"Rent              : ${rent[0]}")
print(f"Revenue           : ${revenue[0]}")
print(f"Distance          : {distance[0]} km")

print("\n--- Randomized Competitor Data ---")
for i in range(num_competitors):
    print(f"Competitor {i+1}: Revenue=${competitor_attractiveness[i]}, Distance={competitor_distances[i]} km")

print("\n--- Sub-scores (Normalized to [0,1]) ---")
for name, score in zip(criteria_names, factor_matrix):
    print(f"{name:15}: {score[0]:.3f}")

print("\n--- AHP-Derived Weights ---")
for name, w in zip(criteria_names, weights):
    print(f"{name:15}: {w:.3f}")

print("\n--- Final Viability Score ---")
print(f"Score (0–1): {final_score:.3f}")
print(f"Score (%): {final_score * 100:.2f}%")
