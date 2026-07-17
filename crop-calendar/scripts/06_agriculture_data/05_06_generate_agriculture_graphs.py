"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Agriculture Visualization
Script  : 05_06_generate_agriculture_graphs.py
Purpose : Generate Agriculture Graphs
============================================================
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = "../../dataset/processed/agriculture/agriculture_clean.csv"

OUTPUT_FOLDER = "../../output/agriculture/graphs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# READ DATA
# ==========================================================

print("=" * 60)
print("GENERATING AGRICULTURE GRAPHS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# GRAPH 1
# TOTAL PRODUCTION BY CROP
# ==========================================================

crop_production = (
    df.groupby("Crop")["Production"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(10,6))

crop_production.plot(kind="bar")

plt.title("Total Production by Crop")
plt.xlabel("Crop")
plt.ylabel("Production")
plt.grid(axis="y")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "01_production_by_crop.png"
    ),
    dpi=300
)

plt.close()

# ==========================================================
# GRAPH 2
# AVERAGE YIELD BY CROP
# ==========================================================

crop_yield = (
    df.groupby("Crop")["Yield"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(10,6))

crop_yield.plot(kind="bar")

plt.title("Average Yield by Crop")
plt.xlabel("Crop")
plt.ylabel("Yield")

plt.grid(axis="y")

plt.tight_layout()

plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "02_average_yield_by_crop.png"

    ),

    dpi=300

)

plt.close()

# ==========================================================
# GRAPH 3
# TOTAL AREA BY CROP
# ==========================================================

crop_area = (

    df.groupby("Crop")["Area"]

    .sum()

    .sort_values(ascending=False)

)

plt.figure(figsize=(10,6))

crop_area.plot(kind="bar")

plt.title("Total Cultivated Area by Crop")

plt.xlabel("Crop")

plt.ylabel("Area")

plt.grid(axis="y")

plt.tight_layout()

plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "03_area_by_crop.png"

    ),

    dpi=300

)

plt.close()

# ==========================================================
# GRAPH 4
# TOP 10 DISTRICTS BY PRODUCTION
# ==========================================================

district_production = (

    df.groupby("District")["Production"]

    .sum()

    .sort_values(ascending=False)

    .head(10)

)

plt.figure(figsize=(10,6))

district_production.plot(kind="bar")

plt.title("Top 10 Districts by Production")

plt.xlabel("District")

plt.ylabel("Production")

plt.grid(axis="y")

plt.tight_layout()

plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "04_top10_district_production.png"

    ),

    dpi=300

)

plt.close()

# ==========================================================
# GRAPH 5
# TOP 10 DISTRICTS BY CULTIVATED AREA
# ==========================================================

district_area = (

    df.groupby("District")["Area"]

    .sum()

    .sort_values(ascending=False)

    .head(10)

)

plt.figure(figsize=(10,6))

district_area.plot(kind="bar")

plt.title("Top 10 Districts by Cultivated Area")

plt.xlabel("District")

plt.ylabel("Area")

plt.grid(axis="y")

plt.tight_layout()

plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "05_top10_district_area.png"

    ),

    dpi=300

)

plt.close()

# ==========================================================
# GRAPH 6
# YEARLY TOTAL PRODUCTION TREND
# ==========================================================

yearly_production = (

    df.groupby("Year")["Production"]

    .sum()

)

plt.figure(figsize=(10,6))

plt.plot(

    yearly_production.index,

    yearly_production.values,

    marker="o",

    linewidth=2

)

plt.title("Yearly Total Production Trend")

plt.xlabel("Year")

plt.ylabel("Production")

plt.grid(True)

plt.tight_layout()

plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "06_yearly_production_trend.png"

    ),

    dpi=300

)

plt.close()

# ==========================================================
# GRAPH 7
# YEARLY AVERAGE YIELD TREND
# ==========================================================

yearly_yield = (

    df.groupby("Year")["Yield"]

    .mean()

)

plt.figure(figsize=(10,6))

plt.plot(

    yearly_yield.index,

    yearly_yield.values,

    marker="o",

    linewidth=2

)

plt.title("Yearly Average Yield Trend")

plt.xlabel("Year")

plt.ylabel("Average Yield")

plt.grid(True)

plt.tight_layout()

plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "07_yearly_yield_trend.png"

    ),

    dpi=300

)

plt.close()

# ==========================================================
# GRAPH 8
# TOTAL PRODUCTION BY SEASON
# ==========================================================

season_production = (

    df.groupby("Season")["Production"]

    .sum()

    .sort_values(ascending=False)

)

plt.figure(figsize=(10,6))

season_production.plot(kind="bar")

plt.title("Total Production by Season")

plt.xlabel("Season")

plt.ylabel("Production")

plt.grid(axis="y")

plt.tight_layout()

plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "08_season_production.png"

    ),

    dpi=300

)

plt.close()

print()

print("=" * 60)
print("ALL AGRICULTURE GRAPHS GENERATED SUCCESSFULLY")
print("=" * 60)

print()

print("Graphs Generated : 8")

print()

print("01_production_by_crop.png")
print("02_average_yield_by_crop.png")
print("03_area_by_crop.png")
print("04_top10_district_production.png")
print("05_top10_district_area.png")
print("06_yearly_production_trend.png")
print("07_yearly_yield_trend.png")
print("08_season_production.png")

print()

print("Saved To :")

print(OUTPUT_FOLDER)