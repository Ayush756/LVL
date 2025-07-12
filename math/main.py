import numpy as np
from flask import request
import json
from scoring import (
    demographic_fit_score,
    poi_amenity_score,
    accessibility_score,
    affordability_score,
    weighted_score,
    normalize_distance
)

from model import gravity_model, huff_model
from normalization import min_max_scale
from ahp import ahp_weights  

json_file_path = 'E:/project/LVL/math/data/input_data.json'

# Load the JSON data from the file
with open(json_file_path, 'r') as f:
    data = json.load(f)

#print("Loaded data:", data)
# data = request.get_json()  # parses JSON into Python dict:contentReference[oaicite:1]{index=1}
candidate = data['candidate']
competitors = data['competitors']

# Data part 1: Candidate location data
cand = data['candidate']
attractiveness = cand['attractiveness']
distance = cand['distance']
population = cand['population']
income = cand['income']
amenities = cand['amenities']
footfall = cand['foot_traffic']
connectivity = cand['connectivity_score']
rent = cand['rent']
revenue = cand['revenue']


#data part competitor data
comps = data['competitors']
comp_attractiveness = [c['attractiveness'] for c in comps]
comp_distances = [c['distance'] for c in comps]
comp_population = [c['population'] for c in comps]
comp_amenities = [c['amenities'] for c in comps]
comp_footfalls = [c['foot_traffic'] for c in comps]

# === 3. Combine candidate + competitors ===
all_attractiveness = [attractiveness] + comp_attractiveness
all_distances = [distance] + comp_distances
all_populations = [population] + comp_population
all_amenities = [amenities] + comp_amenities
all_footfalls = [footfall] + comp_footfalls


# === 4. Compute Huff and Gravity
huff_scores = huff_model(all_attractiveness, all_distances, beta=2)
S_huff = [huff_scores[0]]  # candidate’s share


G_raw = gravity_model(all_populations, all_distances, all_attractiveness, beta=3)
S_grav = [min_max_scale(G_raw)][0]

# === 5. Compute other scores
S_dem = demographic_fit_score(population, income)
S_poi = poi_amenity_score(all_amenities)
S_acc = [min_max_scale(all_footfalls)[0]]
S_aff = affordability_score(rent, revenue)
S_dist = [1 - min_max_scale(all_distances)[0]]  # closer = higher

# === 6. merging similar factor scores
S_dem_all=(S_dem + 4*S_grav[0]) / 5


criteria_names = [
    "demographic", "poi_amenity", "accessibility",
    "affordability", "huff_model", "distance"
]

# === 7. AHP pairwise comparison matrix (customize if needed)
pairwise_matrix = [
        [1,    3,    3,   4,     2,      4],
        [0.33,  1,   2,   1,     0.25,    2],
        [0.33, 0.5,  1,   0.5,   0.33,    1],
        [0.25, 1,    2,   1,     .25,  1.25],
        [0.5,  4,    3,   4,     1,       2],
        [0.25, 0.5,  1,   .8,     0.5,    1]
]
weights = ahp_weights(pairwise_matrix)

print("Weights:", weights)
# === 8. Final score
factor_list = [
    float(S_dem_all),
    float(S_poi[0]),
    float(S_acc[0]),
    float(S_aff),
    float(S_huff[0]),
    float(S_dist[0])
]
print("Factor List:", factor_list)
final_score = weighted_score(factor_list, weights)

print("Final Score: {:.2f}%".format(final_score * 100))

from report_generator import generate_pdf_report

generate_pdf_report(
    factor_list=factor_list,
    criteria_names=criteria_names,
    weights=weights,
    final_score=final_score
)

