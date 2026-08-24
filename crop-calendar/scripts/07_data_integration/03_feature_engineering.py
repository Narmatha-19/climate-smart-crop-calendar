"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Feature Engineering
Script  : 03_feature_engineering.py
Purpose : Create Basic ML Features
============================================================
"""

import os
import pandas as pd
import numpy as np

# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = "../../dataset/final/climate_agriculture_merged.csv"

OUTPUT_FOLDER = "../../dataset/final"

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "climate_agriculture_features.csv"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("=" * 60)
print("FEATURE ENGINEERING")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# TEMPERATURE CATEGORY
# ==========================================================

def temperature_category(temp):

    if temp < 25:
        return "Cool"

    elif temp < 30:
        return "Normal"

    else:
        return "Hot"

df["Temperature_Category"] = df["AvgTemperature"].apply(
    temperature_category
)

# ==========================================================
# RAINFALL CATEGORY
# ==========================================================

def rainfall_category(rain):

    if rain < 800:
        return "Low"

    elif rain < 1200:
        return "Medium"

    else:
        return "High"

df["Rainfall_Category"] = df["TotalRainfall"].apply(
    rainfall_category
)

# ==========================================================
# HUMIDITY CATEGORY
# ==========================================================

def humidity_category(humidity):

    if humidity < 60:
        return "Low"

    elif humidity < 75:
        return "Medium"

    else:
        return "High"

df["Humidity_Category"] = df["AvgHumidity"].apply(
    humidity_category
)

# ==========================================================
# WIND CATEGORY
# ==========================================================

def wind_category(wind):

    if wind < 2:
        return "Low"

    elif wind < 3.5:
        return "Medium"

    else:
        return "High"

df["Wind_Category"] = df["AvgWindSpeed"].apply(
    wind_category
)

# ==========================================================
# YIELD CATEGORY
# ==========================================================
# Computed PER CROP, not with one global 0.33/0.66 split across every crop.
# Different crops have completely different natural yield scales (Sesame
# ~0.5 t/ha vs Sugarcane ~100 t/ha vs Tapioca ~35 t/ha) - a single global
# quantile split would classify almost every Sugarcane record as "High"
# and almost every Sesame record as "Low" regardless of how each actually
# performed relative to its own normal range, so "High/Medium/Low" would
# really just mean "which crop is this" rather than "how well did it do".
# Grouping by Crop first means each record is only ever compared against
# its own crop's history, which is what "yield category" is supposed to
# measure. This matters more now that 25 crops with very different yield
# scales share this one dataset (it was already a latent issue with the
# original 8, just less visible since Sugarcane/Banana were the only
# high-scale outliers).

def yield_category_per_crop(group):

    q1 = group.quantile(0.33)
    q2 = group.quantile(0.66)

    def bucket(y):
        if y <= q1:
            return "Low"
        elif y <= q2:
            return "Medium"
        else:
            return "High"

    return group.apply(bucket)

df["Yield_Category"] = df.groupby("Crop")["Yield"].transform(
    lambda group: yield_category_per_crop(group)
)

# ==========================================================
# SAVE
# ==========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# SUMMARY
# ==========================================================

print()
print("Original Columns :", 19)
print("New Columns      :", len(df.columns))
print()

print("Added Features")

print("- Temperature_Category")
print("- Rainfall_Category")
print("- Humidity_Category")
print("- Wind_Category")
print("- Yield_Category")

print()

print("=" * 60)
print("FEATURE ENGINEERING COMPLETED")
print("=" * 60)

print()

print("Records :", len(df))

print("Saved To")
print(OUTPUT_FILE)