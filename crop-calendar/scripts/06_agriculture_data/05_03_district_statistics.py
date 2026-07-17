"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Agriculture EDA
Script  : 05_03_district_statistics.py
Purpose : Generate district-wise agricultural statistics
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
    "district_statistics.csv"
)

# ==========================================================
# READ DATA
# ==========================================================

print("=" * 60)
print("DISTRICT STATISTICS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# DISTRICT STATISTICS
# ==========================================================

district_stats = df.groupby("District").agg(

    Total_Crops=("Crop", "nunique"),

    Unique_Seasons=("Season", "nunique"),

    Years_Covered=("Year", "nunique"),

    Total_Records=("District", "count"),

    Total_Area=("Area", "sum"),

    Total_Production=("Production", "sum"),

    Average_Yield=("Yield", "mean"),

    Maximum_Yield=("Yield", "max"),

    Minimum_Yield=("Yield", "min")

).reset_index()

# ==========================================================
# ROUND VALUES
# ==========================================================

numeric_columns = [

    "Total_Area",
    "Total_Production",
    "Average_Yield",
    "Maximum_Yield",
    "Minimum_Yield"

]

district_stats[numeric_columns] = district_stats[numeric_columns].round(2)

# ==========================================================
# SORT BY TOTAL PRODUCTION
# ==========================================================

district_stats = district_stats.sort_values(
    by="Total_Production",
    ascending=False
)

# ==========================================================
# ADD RANK
# ==========================================================

district_stats.insert(
    0,
    "Rank",
    range(1, len(district_stats) + 1)
)

# ==========================================================
# SAVE
# ==========================================================

district_stats.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# DISPLAY
# ==========================================================

print("\nTop 10 Districts\n")

print(district_stats.head(10))

print("\n" + "=" * 60)
print("DISTRICT STATISTICS GENERATED SUCCESSFULLY")
print("=" * 60)

print(f"\nTotal Districts : {len(district_stats)}")
print(f"Saved To : {OUTPUT_FILE}")