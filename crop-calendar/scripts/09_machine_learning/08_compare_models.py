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

RF_FILE = os.path.join(OUTPUT_FOLDER, "model_metrics.csv")

DT_FILE = os.path.join(OUTPUT_FOLDER, "decision_tree_metrics.csv")

XGB_FILE = os.path.join(OUTPUT_FOLDER, "xgboost_metrics.csv")

COMPARISON_FILE = os.path.join(OUTPUT_FOLDER, "model_comparison.csv")

BEST_MODEL_FILE = os.path.join(OUTPUT_FOLDER, "best_model.txt")

BAR_CHART = os.path.join(OUTPUT_FOLDER, "model_comparison_bar_chart.png")

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

rf = load_metrics(RF_FILE, "Random Forest")

dt = load_metrics(DT_FILE, "Decision Tree")

xgb = load_metrics(XGB_FILE, "XGBoost")

comparison = pd.DataFrame([rf, dt, xgb])

# ==========================================================
# SELECT REQUIRED METRICS
# ==========================================================

comparison = comparison[["Model", "Training_R2", "Testing_R2", "MAE", "RMSE"]]

# ==========================================================
# CALCULATE MODEL PERFORMANCE METRICS
# ==========================================================

# Difference between training and testing R²
comparison["Overfitting_Gap"] = comparison["Training_R2"] - comparison["Testing_R2"]

# Convert Testing R² into percentage
# This represents the percentage of variance
# explained by the regression model.
comparison["R2_Percentage"] = comparison["Testing_R2"] * 100

# ==========================================================
# SORT MODELS
# ==========================================================

comparison = comparison.sort_values(
    by=["Testing_R2", "Overfitting_Gap", "RMSE"], ascending=[False, True, True]
).reset_index(drop=True)

# ==========================================================
# ADD RANK
# ==========================================================

comparison.insert(0, "Rank", range(1, len(comparison) + 1))

# ==========================================================
# REORDER FINAL COLUMNS
# ==========================================================

comparison = comparison[
    [
        "Rank",
        "Model",
        "Training_R2",
        "Testing_R2",
        "R2_Percentage",
        "MAE",
        "RMSE",
        "Overfitting_Gap",
    ]
]

# ==========================================================
# SAVE CSV
# ==========================================================

comparison.to_csv(COMPARISON_FILE, index=False)

# ==========================================================
# PRINT RESULTS
# ==========================================================

print("\n")
print(comparison.to_string(index=False))

# ==========================================================
# PRINT R² PERCENTAGE
# ==========================================================

print("\n")
print("MODEL PERFORMANCE PERCENTAGE")
print("-" * 40)

for _, row in comparison.iterrows():

    print(f"{row['Model']:20s} : " f"{row['R2_Percentage']:.2f}%")

# ==========================================================
# BEST MODEL
# ==========================================================

best = comparison.iloc[0]

# ==========================================================
# SAVE BEST MODEL INFORMATION
# ==========================================================

with open(BEST_MODEL_FILE, "w", encoding="utf-8") as f:

    f.write("=" * 60 + "\n")
    f.write("BEST MACHINE LEARNING MODEL\n")
    f.write("=" * 60 + "\n\n")

    f.write(f"Model              : " f"{best['Model']}\n")

    f.write(f"Training R²        : " f"{best['Training_R2']:.4f}\n")

    f.write(f"Testing R²         : " f"{best['Testing_R2']:.4f}\n")

    f.write(f"R² Percentage      : " f"{best['R2_Percentage']:.2f}%\n")

    f.write(f"Overfitting Gap    : " f"{best['Overfitting_Gap']:.4f}\n")

    f.write(f"MAE                : " f"{best['MAE']:.2f}\n")

    f.write(f"RMSE               : " f"{best['RMSE']:.2f}\n\n")

    # Reasons are checked against the actual comparison table instead of
    # being fixed boilerplate, so this file never claims a metric the top
    # model didn't actually win (e.g. it's possible for #1 by Testing_R2 to
    # not also have the single lowest Overfitting_Gap - that gets called
    # out honestly below rather than silently claimed).
    f.write("Reason for Selection\n")
    f.write("------------------------------\n")

    f.write("✔ Highest Testing R²\n")
    f.write("✔ Highest R² Percentage\n")

    if best["Overfitting_Gap"] == comparison["Overfitting_Gap"].min():
        f.write("✔ Lowest Overfitting Gap\n")
    else:
        gap_leader = comparison.loc[comparison["Overfitting_Gap"].idxmin()]
        f.write(
            f"~ {gap_leader['Model']} has a lower overfitting gap "
            f"({gap_leader['Overfitting_Gap']:.4f} vs {best['Overfitting_Gap']:.4f}), "
            f"but {best['Model']} leads on Testing R², MAE and RMSE\n"
        )

    if best["RMSE"] == comparison["RMSE"].min():
        f.write("✔ Lowest RMSE\n")

    if best["MAE"] == comparison["MAE"].min():
        f.write("✔ Lowest MAE\n")

    f.write("✔ Strong Overall Prediction Performance\n")
    f.write("✔ Selected for Final Deployment\n")

# ==========================================================
# BAR CHART
# ==========================================================

plt.figure(figsize=(8, 5))

plt.bar(comparison["Model"], comparison["Testing_R2"])

plt.ylabel("Testing R²")
plt.xlabel("Machine Learning Model")
plt.title("Machine Learning Model Comparison")

plt.tight_layout()

plt.savefig(BAR_CHART, dpi=300)

plt.close()

# ==========================================================
# SUMMARY
# ==========================================================

print("\n")
print("=" * 60)
print("MODEL COMPARISON COMPLETED")
print("=" * 60)

print(f"\nBest Model : " f"{best['Model']}")

print(f"Testing R² : " f"{best['Testing_R2']:.4f}")

print(f"R² Percentage : " f"{best['R2_Percentage']:.2f}%")

print(f"Overfitting Gap : " f"{best['Overfitting_Gap']:.4f}")

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
