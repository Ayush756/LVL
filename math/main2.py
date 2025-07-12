from flask import Flask, request, render_template
import plotly.express as px
from scoring import demographic_fit_score, poi_amenity_score, accessibility_score, affordability_score, weighted_score
from model import gravity_model, huff_model
from normalization import min_max_scale
from ahp import ahp_weights
from matplotlib.figure import Figure

app = Flask(__name__)

@app.route('/evaluate', methods=['POST'])
def evaluate_location():
    data = request.get_json()  # parse JSON input:contentReference[oaicite:19]{index=19}
    cand = data['candidate']
    comps = data['competitors']

    # Extract candidate attributes
    attractiveness = cand['attractiveness']
    distance = cand['distance']
    population = cand['population']
    income = cand['income']
    amenities = cand['amenities']
    footfall = cand['footfall']
    connectivity = cand['connectivity']
    rent = cand['rent']
    revenue = cand['revenue']

    # Extract competitors' lists (examples)
    comp_attractiveness = [c['attractiveness'] for c in comps]
    comp_distances = [c['distance'] for c in comps]
    comp_population = [c['population'] for c in comps]

    # Combine for Huff/Gravity
    
    all_attr = [attractiveness] + comp_attractiveness
    all_dist = [distance] + comp_distances
    all_pop = [population] * comp_population

    # Huff and Gravity scores
    huff_scores = huff_model(all_attr, all_dist, beta=2)
    S_huff = huff_scores[0]
    G_raw = gravity_model(all_pop, all_dist, all_attr, beta=2)
    S_grav = min_max_scale(G_raw)[0]

    # Other factor scores
    S_dem = demographic_fit_score(population, income)
    S_poi = poi_amenity_score(amenities)
    S_acc = accessibility_score(footfall, connectivity)
    S_aff = affordability_score(rent, revenue)

    # Merge demographic and gravity as needed
    S_dem_all = (S_dem + 2*S_grav) / 3

    # Distance factor (closer is better)
    S_dist = 1 - min_max_scale([distance])[0]

    # Define criteria and compute AHP weights
    criteria_names = ["demographic","poi_amenity","accessibility","affordability","huff_model","distance"]
    pairwise = [
        [1,    3,    3,   4,     2,  4],
        [0.33,  1,   2,   1,     0.25,  2],
        [0.33, 0.5,  1,   0.5,   0.33,  1],
        [0.25, 0.5,  2,   1,     .25,  1.25],
        [0.5,  4,    3,   4,     1,     2],
        [0.25, 0.5,  1,   .8,     1,    0.25]
    ]
    weights = ahp_weights(pairwise)
    factors = [[S_dem_all, S_poi, S_acc, S_aff, S_huff, S_dist]]
    final_score = weighted_score(factors, weights)[0]

    # --- Generate Charts ---
    # Radar chart for candidate vs competitor (example: using first competitor)
    categories = criteria_names.copy()
    cand_scores = [S_dem_all, S_poi, S_acc, S_aff, S_huff, S_dist]
    comp_scores = []  # compute competitor's factor scores similarly
    # (for brevity, assume comp_scores is filled for each competitor)

    # Example with Plotly Express (single trace shown)
    radar_fig = px.line_polar(r=cand_scores + [cand_scores[0]],
                              theta=categories + [categories[0]],
                              fill='toself',
                              title="Site Metrics Comparison")
    radar_html = radar_fig.to_html(full_html=False)  # HTML for embedding:contentReference[oaicite:20]{index=20}

    # Bar chart of final scores
    names = ["Candidate"] + [f"Competitor {i+1}" for i in range(len(comps))]
    scores = [final_score] + [weighted_score([[fact_val_list]], weights)[0] for fact_val_list in comp_scores]
    bar_fig = px.bar(x=names, y=scores, title="Viability Score Comparison")
    bar_html = bar_fig.to_html(full_html=False)

    # Render results in a template (passing chart HTML and score)
    return render_template('results.html',
                           final_score=final_score,
                           radar_chart=radar_html,
                           bar_chart=bar_html)
