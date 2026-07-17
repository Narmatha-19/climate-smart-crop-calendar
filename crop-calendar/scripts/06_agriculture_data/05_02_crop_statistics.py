import os
import pandas as pd
import numpy as np

# ==========================================
# PATHS
# ==========================================

INPUT_FILE = "../../dataset/processed/agriculture/agriculture_clean.csv"

OUTPUT_FOLDER = "../../output/agriculture/analysis"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OVERALL_FILE = os.path.join(
    OUTPUT_FOLDER,
    "crop_statistics.csv"
)

DISTRICT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "crop_district_statistics.csv"
)

# ==========================================
# READ DATA
# ==========================================

print("=" * 60)
print("CROP STATISTICS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================
# STABILITY FUNCTION
# ==========================================

def classify_stability(cv):

    if pd.isna(cv):
        return "Insufficient Data"

    if cv < 10:
        return "Highly Stable"

    elif cv < 20:
        return "Stable"

    elif cv < 30:
        return "Moderately Variable"

    else:
        return "Highly Variable"

# ==========================================
# OVERALL CROP STATISTICS
# ==========================================

overall = df.groupby("Crop").agg(

    Total_Area=("Area", "sum"),

    Total_Production=("Production", "sum"),

    Average_Yield=("Yield", "mean"),

    Maximum_Yield=("Yield", "max"),

    Minimum_Yield=("Yield", "min"),

    Total_Records=("Crop", "count")

).reset_index()

overall = overall.round(2)

overall = overall.sort_values(
    "Total_Production",
    ascending=False
)

overall.to_csv(
    OVERALL_FILE,
    index=False
)

# ==========================================
# CROP × DISTRICT STATISTICS
# ==========================================

district = df.groupby(

    ["Crop", "District"]

).agg(

    Years_Covered=("Year", "nunique"),

    Total_Area=("Area", "sum"),

    Total_Production=("Production", "sum"),

    Average_Yield=("Yield", "mean"),

    Yield_Std=("Yield", "std"),

    Maximum_Yield=("Yield", "max"),

    Minimum_Yield=("Yield", "min"),

    Records=("Yield", "count")

).reset_index()

district["CV_Percentage"] = (
    district["Yield_Std"] /
    district["Average_Yield"]
) * 100

district["Yield_Stability"] = district["CV_Percentage"].apply(classify_stability)

district = district.round(2)

district = district.sort_values(

    ["Crop", "Total_Production"],

    ascending=[True, False]

)

district.to_csv(

    DISTRICT_FILE,

    index=False

)

# ==========================================
# SUMMARY
# ==========================================

print()

print("Overall Crop Statistics :", len(overall))

print("Crop-District Statistics :", len(district))

print()

print("Files Saved")

print("----------------------------")

print(OVERALL_FILE)

print(DISTRICT_FILE)

print()

print("=" * 60)

print("CROP STATISTICS COMPLETED SUCCESSFULLY")

print("=" * 60)