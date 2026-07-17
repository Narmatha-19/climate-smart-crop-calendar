"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Final Dataset EDA
Script  : 01_dataset_overview.py
Purpose : Overview of Final Feature Engineered Dataset
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

# ==========================================================
# LOAD DATA
# ==========================================================

print("=" * 60)
print("FINAL DATASET OVERVIEW")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# BASIC INFORMATION
# ==========================================================

print("\nBasic Information")
print("-" * 40)

print("Total Records    :", len(df))
print("Total Columns    :", len(df.columns))
print("Districts        :", df["District"].nunique())
print("Crops            :", df["Crop"].nunique())
print("Seasons          :", df["Season"].nunique())
print("Years            :", df["Year"].min(), "-", df["Year"].max())

# ==========================================================
# MISSING VALUES
# ==========================================================

print("\nMissing Values")
print("-" * 40)

missing = df.isnull().sum()

print(missing)

# ==========================================================
# DATA TYPES
# ==========================================================

print("\nColumn Data Types")
print("-" * 40)

print(df.dtypes)

# ==========================================================
# UNIQUE VALUES
# ==========================================================

print("\nUnique Categories")
print("-" * 40)

print("Temperature Categories :", sorted(df["Temperature_Category"].unique()))
print("Rainfall Categories    :", sorted(df["Rainfall_Category"].unique()))
print("Humidity Categories    :", sorted(df["Humidity_Category"].unique()))
print("Wind Categories        :", sorted(df["Wind_Category"].unique()))
print("Yield Categories       :", sorted(df["Yield_Category"].unique()))

# ==========================================================
# NUMERIC SUMMARY
# ==========================================================

print("\nNumeric Summary")
print("-" * 40)

summary = df.describe().round(2)

print(summary)

# ==========================================================
# SAVE REPORTS
# ==========================================================

summary.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "numeric_summary.csv"
    )
)

missing.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "missing_values.csv"
    )
)

# ==========================================================
# COMPLETED
# ==========================================================

print("\n" + "=" * 60)
print("DATASET OVERVIEW COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nReports Saved To")
print(OUTPUT_FOLDER)