import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from io import BytesIO
import os

def create_radar_chart_image(factor_list, criteria_names):
    num_vars = len(criteria_names)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    scores = factor_list + [factor_list[0]]
    angles += [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.fill(angles, scores, color='skyblue', alpha=0.4)
    ax.plot(angles, scores, color='blue', linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria_names, fontsize=10)
    ax.set_yticklabels([])
    ax.set_title("Viability Radar Chart", size=12, pad=10)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='PNG')
    plt.close(fig)
    buf.seek(0)
    return buf

def create_bar_chart_image(factor_list, criteria_names):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(criteria_names, factor_list, color='seagreen')
    ax.set_ylim(0, 1)
    ax.set_title("Factor-wise Normalized Scores")
    ax.set_ylabel("Score (0-1)")
    ax.set_xticklabels(criteria_names, rotation=30)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='PNG')
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_pdf_report(factor_list, criteria_names, weights, final_score, output_path="viability_report.pdf"):
    radar_buf = create_radar_chart_image(factor_list, criteria_names)
    bar_buf = create_bar_chart_image(factor_list, criteria_names)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Coffee Shop Viability Report", ln=1, align="C")

    pdf.set_font("Arial", '', 12)
    pdf.ln(4)
    pdf.cell(0, 10, f"Final Viability Score: {final_score:.2%}", ln=1)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Factor Scores & Weights:", ln=1)

    pdf.set_font("Arial", '', 11)
    for name, score, weight in zip(criteria_names, factor_list, weights):
        pdf.cell(0, 8, f"{name.capitalize():<15} Score: {score:.3f} | Weight: {weight:.2f}", ln=1)

    pdf.ln(5)
    # Save radar chart inline
    radar_path = "temp_radar.png"
    with open(radar_path, "wb") as f:
        f.write(radar_buf.read())
    pdf.image(radar_path, x=30, w=150)

    pdf.ln(10)
    # Save bar chart inline
    bar_path = "temp_bar.png"
    with open(bar_path, "wb") as f:
        f.write(bar_buf.read())
    pdf.image(bar_path, x=30, w=150)

    pdf.output(output_path)

    # Clean up temp images
    os.remove(radar_path)
    os.remove(bar_path)

    print(f"✅ PDF Report saved to: {output_path}")
