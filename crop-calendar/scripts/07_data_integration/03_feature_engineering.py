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

yield_q1 = df["Yield"].quantile(0.33)
yield_q2 = df["Yield"].quantile(0.66)

def yield_category(y):

    if y <= yield_q1:
        return "Low"

    elif y <= yield_q2:
        return "Medium"

    else:
        return "High"

df["Yield_Category"] = df["Yield"].apply(
    yield_category
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