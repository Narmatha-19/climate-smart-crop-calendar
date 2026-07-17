"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Final Dataset EDA
Script  : 05_correlation_analysis.py
Purpose : Correlation Analysis of Numerical Features
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
    "correlation_matrix.csv"
)

# ==========================================================
# READ DATASET
# ==========================================================

print("=" * 60)
print("CORRELATION ANALYSIS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# NUMERIC COLUMNS
# ==========================================================

numeric_columns = [

    "Area",

    "Production",

    "Yield",

    "AvgTemperature",

    "MaxTemperature",

    "MinTemperature",

    "TotalRainfall",

    "AvgRainfall",

    "MaxRainfall",

    "AvgHumidity",

    "AvgWindSpeed",

    "RainyDays",

    "TemperatureStd",

    "RainfallStd"

]

# ==========================================================
# CORRELATION MATRIX
# ==========================================================

correlation = (
    df[numeric_columns]
    .corr(method="pearson")
    .round(2)
)

# ==========================================================
# SAVE
# ==========================================================

correlation.to_csv(
    OUTPUT_FILE
)

# ==========================================================
# DISPLAY
# ==========================================================

print()
print("Correlation Matrix")
print("-" * 60)

print(correlation)

# ==========================================================
# STRONGEST RELATIONSHIP WITH YIELD
# ==========================================================

yield_corr = (
    correlation["Yield"]
    .drop("Yield")
    .sort_values(
        key=lambda x: abs(x),
        ascending=False
    )
)

print()

print("=" * 60)
print("FEATURES MOST RELATED TO YIELD")
print("=" * 60)

print()

print(yield_corr)

# ==========================================================
# SUMMARY
# ==========================================================

print()

print("=" * 60)
print("CORRELATION ANALYSIS COMPLETED")
print("=" * 60)

print()

print("Numeric Features :", len(numeric_columns))

print("Correlation Matrix Size :",
      correlation.shape[0],
      "x",
      correlation.shape[1])

print()

print("Saved To")

print(OUTPUT_FILE)

print()

print("=" * 60)