"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Agriculture EDA
Script  : 05_04_yearly_statistics.py
Purpose : Generate year-wise agricultural statistics
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
    "yearly_statistics.csv"
)

# ==========================================================
# READ DATA
# ==========================================================

print("=" * 60)
print("YEARLY AGRICULTURE STATISTICS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# YEARLY STATISTICS
# ==========================================================

yearly_stats = df.groupby("Year").agg(

    Total_Districts=("District", "nunique"),

    Total_Crops=("Crop", "nunique"),

    Total_Seasons=("Season", "nunique"),

    Total_Records=("Year", "count"),

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

yearly_stats[numeric_columns] = yearly_stats[numeric_columns].round(2)

# ==========================================================
# SORT
# ==========================================================

yearly_stats = yearly_stats.sort_values("Year")

# ==========================================================
# SAVE
# ==========================================================

yearly_stats.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# DISPLAY
# ==========================================================

print()

print(yearly_stats)

print()

print("=" * 60)
print("YEARLY STATISTICS GENERATED SUCCESSFULLY")
print("=" * 60)

print(f"\nTotal Years : {len(yearly_stats)}")
print(f"Year Range  : {yearly_stats['Year'].min()} - {yearly_stats['Year'].max()}")
print(f"Saved To    : {OUTPUT_FILE}")