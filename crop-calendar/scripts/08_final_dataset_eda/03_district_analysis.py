"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Final Dataset EDA
Script  : 03_district_analysis.py
Purpose : District-wise Agricultural Analysis
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
    "district_analysis.csv"
)

# ==========================================================
# LOAD DATA
# ==========================================================

print("=" * 60)
print("DISTRICT ANALYSIS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# DISTRICT ANALYSIS
# ==========================================================

district_stats = (
    df.groupby("District")
    .agg(
        Total_Records=("District", "count"),
        Total_Crops=("Crop", "nunique"),
        Years=("Year", "nunique"),
        Seasons=("Season", "nunique"),
        Average_Area=("Area", "mean"),
        Average_Production=("Production", "mean"),
        Average_Yield=("Yield", "mean"),
        Maximum_Yield=("Yield", "max"),
        Minimum_Yield=("Yield", "min"),
        Avg_Temperature=("AvgTemperature", "mean"),
        Avg_Rainfall=("TotalRainfall", "mean"),
        Avg_Humidity=("AvgHumidity", "mean")
    )
    .round(2)
    .reset_index()
)

# ==========================================================
# SORT BY YIELD
# ==========================================================

district_stats = district_stats.sort_values(
    by="Average_Yield",
    ascending=False
).reset_index(drop=True)

# ==========================================================
# ADD RANK
# ==========================================================

district_stats.insert(
    0,
    "Rank",
    range(1, len(district_stats) + 1)
)

# ==========================================================
# SAVE COMPLETE DATASET (ALL DISTRICTS)
# ==========================================================

district_stats.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# FILTER RELIABLE DISTRICTS
# ==========================================================

display_stats = district_stats[
    district_stats["Total_Records"] >= 50
].copy()

display_stats = display_stats.sort_values(
    by="Average_Yield",
    ascending=False
).reset_index(drop=True)

# Remove old rank
display_stats.drop(columns=["Rank"], inplace=True)

# Add fresh rank
display_stats.insert(
    0,
    "Rank",
    range(1, len(display_stats) + 1)
)

# ==========================================================
# DISPLAY
# ==========================================================

print()
print("Top 10 Reliable Districts (Minimum 50 Records)")
print()

print(display_stats.head(10).to_string(index=False))

# ==========================================================
# SUMMARY
# ==========================================================

print()

print("=" * 60)
print("DISTRICT ANALYSIS COMPLETED")
print("=" * 60)

print()

print("Total Districts (Overall) :", len(district_stats))
print("Reliable Districts        :", len(display_stats))

print()

print("Saved To")
print(OUTPUT_FILE)