import numpy as np
from flask import request
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

import pandas as pd
from sqlalchemy import create_engine

# --- Competitors from database ---
user = 'kishor'
password = 'kishor'
host = 'localhost'
port = '5432'
database = 'LVL'
table_name = 'competitors'

connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)
df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
comps = df.to_dict(orient='records')

#EDIT HERE 
# Data part 1: Candidate location data
cand = data['candidate']
distance = cand['distance']
population = cand['population']
amenities = cand['amenities']
footfalls = cand['foot_traffic']
varieties
cost 
pop_grid 


#data part competitor data
comp_names = np.array(df['name'])
comp_capacities = np.array(df['capacity'])
comp_varieties = np.array(df['variety'])
comp_populations = np.array(df['population'])
comp_pop_grids = np.array(df['popGrid'])
comp_distances = np.array(df['distance'])
comp_costs = np.array(df['cost'])

#=== Attraciveness compilation
        ###attractiveness 
comp_attractiveness =comp_costs*10+ comp_populations*0.5 + comp_varieties*20+ comp_capacities*3+comp_pop_grids*5

# === 3. Combine candidate + competitors ===
all_attractiveness = [attractiveness] + comp_attractiveness
all_distances = [distance] + comp_distances


# === 4. Compute Huff and Gravity
huff_scores = huff_model(all_attractiveness, all_distances, beta=2)
S_huff = [huff_scores[0]]  # candidate’s share


G_raw = gravity_model(all_populations, all_distances, all_attractiveness, beta=3)
S_grav = [min_max_scale(G_raw)][0]

# === 5. Compute other scores
S_dem = demographic_fit_score(population)
S_poi = poi_amenity_score(amenities)
S_acc = min_max_scale(footfalls)
S_dist = [1 - min_max_scale(all_distances)[0]]  # closer = higher

# === 6. merging similar factor scores
S_dem_all=(S_dem + 4*S_grav[0]) / 5


criteria_names = [
    "demographic", "poi_amenity", "accessibility", "huff_model", "distance"
]

# === 7. AHP pairwise comparison matrix (customize if needed)
pairwise_matrix = [
        [1,    3,    3,      2,      4],
        [0.33,  1,   2,     0.25,    2],
        [0.33, 0.5,  1,     0.33,    1],
        [0.5,  4,    3,      1,      2],
        [0.25, 0.5,  1,      0.5,    1]
]
weights = ahp_weights(pairwise_matrix)

print("Weights:", weights)
# === 8. Final score
factor_list = [
    float(S_dem_all),
    float(S_poi),
    float(S_acc),
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