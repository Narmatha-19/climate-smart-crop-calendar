"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Data Integration
Script  : 02_validate_merged_dataset.py
Purpose : Validate Merged Climate + Agriculture Dataset
============================================================
"""

import os
import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = "../../dataset/final/climate_agriculture_merged.csv"

OUTPUT_FOLDER = "../../output/data_integration"

REPORT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "merged_dataset_validation_report.txt"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("=" * 60)
print("MERGED DATASET VALIDATION")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# BASIC INFORMATION
# ==========================================================

print()
print("Total Records     :", len(df))
print("Total Columns     :", len(df.columns))
print("Districts         :", df["District"].nunique())
print("Years             :", df["Year"].min(), "-", df["Year"].max())
print("Crops             :", df["Crop"].nunique())
print("Seasons           :", df["Season"].nunique())

# ==========================================================
# MISSING VALUES
# ==========================================================

print()
print("=" * 60)
print("MISSING VALUES")
print("=" * 60)

missing = df.isnull().sum()

print(missing)

# ==========================================================
# DUPLICATES
# ==========================================================

duplicates = df.duplicated().sum()

print()
print("Duplicate Rows :", duplicates)

# ==========================================================
# DATA TYPES
# ==========================================================

print()
print("=" * 60)
print("COLUMN DATA TYPES")
print("=" * 60)

print(df.dtypes)

# ==========================================================
# NUMERIC SUMMARY
# ==========================================================

print()
print("=" * 60)
print("NUMERIC SUMMARY")
print("=" * 60)

print(df.describe())

# ==========================================================
# SAVE REPORT
# ==========================================================

with open(REPORT_FILE, "w", encoding="utf-8") as f:

    f.write("MERGED DATASET VALIDATION REPORT\n")
    f.write("=" * 50 + "\n\n")

    f.write(f"Total Records : {len(df)}\n")
    f.write(f"Total Columns : {len(df.columns)}\n")
    f.write(f"Districts     : {df['District'].nunique()}\n")
    f.write(f"Years         : {df['Year'].min()} - {df['Year'].max()}\n")
    f.write(f"Crops         : {df['Crop'].nunique()}\n")
    f.write(f"Seasons       : {df['Season'].nunique()}\n\n")

    f.write("Missing Values\n")
    f.write("-" * 50 + "\n")
    f.write(missing.to_string())

    f.write("\n\nDuplicate Rows : ")
    f.write(str(duplicates))

    f.write("\n\nData Types\n")
    f.write("-" * 50 + "\n")
    f.write(df.dtypes.to_string())

print()
print("=" * 60)
print("VALIDATION COMPLETED SUCCESSFULLY")
print("=" * 60)

print()
print("Validation Report Saved To")
print(REPORT_FILE)