"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Agriculture EDA
Script  : 05_05_season_statistics.py
Purpose : Generate season-wise agricultural statistics
============================================================
"""

import os
import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = "../../dataset/processed/agriculture/agriculture_clean.csv"

OUTPUT_FOLDER = "../../output/agriculture/analysis"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "season_statistics.csv"
)

# ==========================================================
# READ DATA
# ==========================================================

print("=" * 60)
print("SEASON STATISTICS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# SEASON STATISTICS
# ==========================================================

season_stats = df.groupby("Season").agg(

    Total_Districts=("District", "nunique"),

    Total_Crops=("Crop", "nunique"),

    Years_Covered=("Year", "nunique"),

    Total_Records=("Season", "count"),

    Total_Area=("Area", "sum"),

    Total_Production=("Production", "sum"),

    Average_Yield=("Yield", "mean"),

    Median_Yield=("Yield", "median"),

    Maximum_Yield=("Yield", "max"),

    Minimum_Yield=("Yield", "min")

).reset_index()

# ==========================================================
# ROUND NUMERIC VALUES
# ==========================================================

numeric_columns = [

    "Total_Area",
    "Total_Production",
    "Average_Yield",
    "Median_Yield",
    "Maximum_Yield",
    "Minimum_Yield"

]

season_stats[numeric_columns] = season_stats[numeric_columns].round(2)

# ==========================================================
# SORT BY PRODUCTION
# ==========================================================

season_stats = season_stats.sort_values(

    by="Total_Production",

    ascending=False

)

# ==========================================================
# ADD RANK
# ==========================================================

season_stats.insert(

    0,

    "Rank",

    range(1, len(season_stats) + 1)

)

# ==========================================================
# SAVE
# ==========================================================

season_stats.to_csv(

    OUTPUT_FILE,

    index=False

)

# ==========================================================
# DISPLAY
# ==========================================================

print()

print(season_stats)

print()

print("=" * 60)
print("SEASON STATISTICS GENERATED SUCCESSFULLY")
print("=" * 60)

print()

print(f"Total Seasons : {len(season_stats)}")
print(f"Saved To : {OUTPUT_FILE}")