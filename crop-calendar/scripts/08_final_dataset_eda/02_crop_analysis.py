"""
============================================================
FINAL DATASET EDA
Crop Analysis
============================================================
"""

import os
import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = "../../dataset/final/climate_agriculture_features.csv"

OUTPUT_FOLDER = "../../output/final_dataset_eda"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "crop_analysis.csv"
)

# ==========================================================
# READ DATA
# ==========================================================

print("=" * 60)
print("CROP ANALYSIS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# ANALYSIS
# ==========================================================

crop_stats = (
    df.groupby("Crop")
    .agg(
        Total_Records=("Crop", "count"),
        Districts=("District", "nunique"),
        Years=("Year", "nunique"),
        Average_Area=("Area", "mean"),
        Average_Production=("Production", "mean"),
        Average_Yield=("Yield", "mean"),
        Maximum_Yield=("Yield", "max"),
        Minimum_Yield=("Yield", "min")
    )
    .round(2)
    .sort_values(
        by="Average_Yield",
        ascending=False
    )
    .reset_index()
)

crop_stats.insert(
    0,
    "Rank",
    range(1, len(crop_stats) + 1)
)

# ==========================================================
# DISPLAY
# ==========================================================

print()
print(crop_stats)

# ==========================================================
# SAVE
# ==========================================================

crop_stats.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# SUMMARY
# ==========================================================

print()
print("=" * 60)
print("CROP ANALYSIS COMPLETED")
print("=" * 60)

print()

print("Total Crops :", len(crop_stats))

print("Saved To")
print(OUTPUT_FILE)