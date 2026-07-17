"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Final Dataset EDA
Script  : 04_climate_relationship_analysis.py
Purpose : Climate Relationship Analysis
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
    "climate_relationship_analysis.csv"
)

# ==========================================================
# READ DATASET
# ==========================================================

print("=" * 60)
print("CLIMATE RELATIONSHIP ANALYSIS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================================
# STORE RESULTS
# ==========================================================

results = []

# ==========================================================
# TEMPERATURE
# ==========================================================

temp = (
    df.groupby("Temperature_Category")
    .agg(
        Records=("Temperature_Category", "count"),
        Average_Value=("AvgTemperature", "mean"),
        Average_Yield=("Yield", "mean"),
        Average_Production=("Production", "mean"),
    )
    .round(2)
    .reset_index()
)

temp.rename(columns={"Temperature_Category": "Category"}, inplace=True)
temp["Climate_Factor"] = "Temperature"

results.append(temp)

# ==========================================================
# RAINFALL
# ==========================================================

rain = (
    df.groupby("Rainfall_Category")
    .agg(
        Records=("Rainfall_Category", "count"),
        Average_Value=("TotalRainfall", "mean"),
        Average_Yield=("Yield", "mean"),
        Average_Production=("Production", "mean"),
    )
    .round(2)
    .reset_index()
)

rain.rename(columns={"Rainfall_Category": "Category"}, inplace=True)
rain["Climate_Factor"] = "Rainfall"

results.append(rain)

# ==========================================================
# HUMIDITY
# ==========================================================

humidity = (
    df.groupby("Humidity_Category")
    .agg(
        Records=("Humidity_Category", "count"),
        Average_Value=("AvgHumidity", "mean"),
        Average_Yield=("Yield", "mean"),
        Average_Production=("Production", "mean"),
    )
    .round(2)
    .reset_index()
)

humidity.rename(columns={"Humidity_Category": "Category"}, inplace=True)
humidity["Climate_Factor"] = "Humidity"

results.append(humidity)

# ==========================================================
# WIND
# ==========================================================

wind = (
    df.groupby("Wind_Category")
    .agg(
        Records=("Wind_Category", "count"),
        Average_Value=("AvgWindSpeed", "mean"),
        Average_Yield=("Yield", "mean"),
        Average_Production=("Production", "mean"),
    )
    .round(2)
    .reset_index()
)

wind.rename(columns={"Wind_Category": "Category"}, inplace=True)
wind["Climate_Factor"] = "Wind"

results.append(wind)

# ==========================================================
# MERGE ALL RESULTS
# ==========================================================

final_df = pd.concat(results, ignore_index=True)

final_df = final_df[
    [
        "Climate_Factor",
        "Category",
        "Records",
        "Average_Value",
        "Average_Yield",
        "Average_Production",
    ]
]

final_df = final_df.sort_values(
    ["Climate_Factor", "Category"]
).reset_index(drop=True)

# ==========================================================
# SAVE
# ==========================================================

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# DISPLAY
# ==========================================================

print()
print(final_df.to_string(index=False))

# ==========================================================
# SUMMARY
# ==========================================================

print()
print("=" * 60)
print("CLIMATE RELATIONSHIP ANALYSIS COMPLETED")
print("=" * 60)

print()

print("Total Records :", len(df))

print("Climate Factors Analysed :", final_df["Climate_Factor"].nunique())

print("Output Rows :", len(final_df))

print()

print("Saved To")

print(OUTPUT_FILE)

print()

print("=" * 60)