"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Machine Learning
Script  : 01_prepare_ml_dataset.py
Purpose : Prepare ML Dataset
============================================================
"""

import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = "../../dataset/final/climate_agriculture_features.csv"

OUTPUT_FOLDER = "../../dataset/final"
MODEL_FOLDER = "../../models"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "ml_dataset.csv"
)

# ==========================================================
# LOAD DATA
# ==========================================================

print("=" * 60)
print("PREPARING MACHINE LEARNING DATASET")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print("\nOriginal Records :", len(df))
print("Original Columns :", len(df.columns))

# ==========================================================
# REMOVE STATE COLUMN
# ==========================================================

if "State" in df.columns:
    df.drop(columns=["State"], inplace=True)

# ==========================================================
# ENCODE ALL CATEGORICAL FEATURES
# ==========================================================

categorical_columns = [

    "District",
    "Crop",
    "Season",
    "Temperature_Category",
    "Rainfall_Category",
    "Humidity_Category",
    "Wind_Category",
    "Yield_Category"

]

encoders = {}

for col in categorical_columns:

    encoder = LabelEncoder()

    df[col] = encoder.fit_transform(df[col].astype(str))

    encoders[col] = encoder

    joblib.dump(
        encoder,
        os.path.join(MODEL_FOLDER, f"{col}_encoder.pkl")
    )

# ==========================================================
# SAVE DATASET
# ==========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# SUMMARY
# ==========================================================

print("\n")
print("=" * 60)
print("ML DATASET CREATED")
print("=" * 60)

print("\nRecords :", len(df))
print("Columns :", len(df.columns))

print("\nEncoded Columns")

for col in categorical_columns:
    print("-", col)

print("\nSaved Dataset")
print(OUTPUT_FILE)

print("\nSaved Encoders")
print(MODEL_FOLDER)

print("\n")
print("=" * 60)
print("PREPARATION COMPLETED SUCCESSFULLY")
print("=" * 60)