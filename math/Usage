# example_usage.py
import numpy as np
from ahp import ahp_weights
from scoring import (demographic_fit_score, competition_score, poi_amenity_score, accessibility_score, affordability_score, weighted_score)

# --- Synthetic demo data for 3 locations (e.g., areas near Kathmandu University) ---

# Population (e.g. within a 1 km radius)
populations = [12000, 8000, 15000]        # e.g. higher = more potential customers
# Average income in area (in USD)
incomes = [500, 300, 700]               # e.g. higher = more spending power

# Competitor counts (number of similar coffee shops nearby)
competitors = [3, 10, 5]                # more competitors is worse

# Nearby amenities count (POIs like shops, transit, parks within walking distance)
amenities = [20, 5, 15]               # more amenities = better environment

# Footfall (estimated daily pedestrian traffic) and connectivity (e.g. transit stops)
footfalls = [1000, 300, 2000]         # higher means more people passing by
connectivity = [5, 2, 8]             # number of transit stops or road intersections

# Rent (monthly) vs expected monthly revenue
rents = [1000, 800, 1200]            # e.g. commercial rent in USD
revenues = [3000, 1500, 5000]        # e.g. estimated revenue if shop is open

# Compute individual factor scores (arrays of length 3)
dem_score = demographic_fit_score(populations, incomes)
comp_score = competition_score(competitors)
poi_score = poi_amenity_score(amenities)
acc_score = accessibility_score(footfalls, connectivity)
aff_score = affordability_score(rents, revenues)

print("Demographic Fit Scores:     ", dem_score)
print("Competition Scores:         ", comp_score)
print("POI/Amenity Scores:         ", poi_score)
print("Accessibility Scores:       ", acc_score)
print("Affordability Scores:       ", aff_score)

# --- AHP weights for factors ---
# Example pairwise comparison matrix for 5 factors (row = factor i vs column = factor j)
#         Dem   Comp  POI   Acc   Aff
ahp_matrix = [
    [1,     3,    1/2,  1,    2   ],  # Demographic vs others
    [1/3,   1,    1/5,  1/2,  1   ],  # Competition
    [2,     5,    1,    3,    4   ],  # Amenities
    [1,     2,    1/3,  1,    2   ],  # Accessibility
    [1/2,   1,    1/4,  1/2,  1   ]   # Affordability
]
weights = ahp_weights(ahp_matrix)
print("AHP weights (Dem, Comp, POI, Acc, Aff):", np.round(weights, 3))

# Compute final viability score for each location
factor_scores = np.vstack([dem_score, comp_score, poi_score, acc_score, aff_score])
# weighted_score expects factor_scores as list of score lists
final_scores = weighted_score(factor_scores, weights)
print("Final Viability Scores:    ", np.round(final_scores, 3))
