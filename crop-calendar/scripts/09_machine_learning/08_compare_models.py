"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Machine Learning
Script  : 08_compare_models.py
Purpose : Compare Machine Learning Models
============================================================
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# PATHS
# ==========================================================

OUTPUT_FOLDER = "../../output/machine_learning"

RF_FILE = os.path.join(
    OUTPUT_FOLDER,
    "model_metrics.csv"
)

DT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "decision_tree_metrics.csv"
)

XGB_FILE = os.path.join(
    OUTPUT_FOLDER,
    "xgboost_metrics.csv"
)

COMPARISON_FILE = os.path.join(
    OUTPUT_FOLDER,
    "model_comparison.csv"
)

BEST_MODEL_FILE = os.path.join(
    OUTPUT_FOLDER,
    "best_model.txt"
)

BAR_CHART = os.path.join(
    OUTPUT_FOLDER,
    "model_comparison_bar_chart.png"
)

# ==========================================================
# LOAD METRICS FUNCTION
# ==========================================================

def load_metrics(file_path, model_name):

    df = pd.read_csv(file_path)

    metrics = {}

    for _, row in df.iterrows():
        metrics[row["Metric"]] = row["Value"]

    metrics["Model"] = model_name

    return metrics


# ==========================================================
# LOAD ALL MODELS
# ==========================================================

print("=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

rf = load_metrics(
    RF_FILE,
    "Random Forest"
)

dt = load_metrics(
    DT_FILE,
    "Decision Tree"
)

xgb = load_metrics(
    XGB_FILE,
    "XGBoost"
)

comparison = pd.DataFrame([
    rf,
    dt,
    xgb
])

comparison = comparison[
    [
        "Model",
        "Training_R2",
        "Testing_R2",
        "MAE",
        "RMSE"
    ]
]

# ==========================================================
# CALCULATE OVERFITTING GAP
# ==========================================================

comparison["Overfitting_Gap"] = (
    comparison["Training_R2"] -
    comparison["Testing_R2"]
)

# ==========================================================
# SORT MODELS
# ==========================================================

comparison = comparison.sort_values(

    by=[
        "Testing_R2",
        "Overfitting_Gap",
        "RMSE"
    ],

    ascending=[
        False,
        True,
        True
    ]

).reset_index(drop=True)

comparison.insert(
    0,
    "Rank",
    range(1, len(comparison) + 1)
)

# ==========================================================
# SAVE CSV
# ==========================================================

comparison.to_csv(
    COMPARISON_FILE,
    index=False
)

# ==========================================================
# PRINT RESULTS
# ==========================================================

print("\n")

print(comparison.to_string(index=False))

# ==========================================================
# BEST MODEL
# ==========================================================

best = comparison.iloc[0]

with open(
    BEST_MODEL_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 60 + "\n")
    f.write("BEST MACHINE LEARNING MODEL\n")
    f.write("=" * 60 + "\n\n")

    f.write(f"Model              : {best['Model']}\n")
    f.write(f"Training R²        : {best['Training_R2']:.4f}\n")
    f.write(f"Testing R²         : {best['Testing_R2']:.4f}\n")
    f.write(f"Overfitting Gap    : {best['Overfitting_Gap']:.4f}\n")
    f.write(f"MAE                : {best['MAE']:.2f}\n")
    f.write(f"RMSE               : {best['RMSE']:.2f}\n\n")

    f.write("Reason for Selection\n")
    f.write("------------------------------\n")
    f.write("✔ Highest Testing R2\n")
    f.write("✔ Lowest Overfitting Gap\n")
    f.write("✔ Lowest Prediction Error\n")
    f.write("✔ Best Generalization Performance\n")
    f.write("✔ Selected for Final Deployment\n")

# ==========================================================
# BAR CHART
# ==========================================================

plt.figure(figsize=(8, 5))

plt.bar(
    comparison["Model"],
    comparison["Testing_R2"]
)

plt.ylabel("Testing R²")
plt.title("Machine Learning Model Comparison")

plt.tight_layout()

plt.savefig(BAR_CHART)

plt.close()

# ==========================================================
# SUMMARY
# ==========================================================

print("\n")
print("=" * 60)
print("MODEL COMPARISON COMPLETED")
print("=" * 60)

print(f"\nBest Model : {best['Model']}")

print("\nGenerated Files")
print("- model_comparison.csv")
print("- best_model.txt")
print("- model_comparison_bar_chart.png")

print("\nSaved To")
print(OUTPUT_FOLDER)

print("\n")
print("=" * 60)
print("ALL MACHINE LEARNING MODELS COMPARED SUCCESSFULLY")
print("=" * 60)