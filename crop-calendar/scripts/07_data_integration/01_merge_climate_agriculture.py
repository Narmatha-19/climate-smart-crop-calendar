"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Data Integration
Script  : 01_merge_climate_agriculture.py
Purpose : Merge Climate and Agriculture Datasets
============================================================
"""

import os
import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

CLIMATE_FILE = "../../output/climate_intelligence/yearly_summary.csv"
AGRI_FILE = "../../dataset/processed/agriculture/agriculture_clean.csv"
MAPPING_FILE = "../../dataset/final/district_mapping.csv"

OUTPUT_FOLDER = "../../dataset/final"
OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "climate_agriculture_merged.csv"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# READ DATA
# ==========================================================

print("=" * 60)
print("MERGING CLIMATE AND AGRICULTURE DATA")
print("=" * 60)

climate = pd.read_csv(CLIMATE_FILE)
agri = pd.read_csv(AGRI_FILE)
mapping = pd.read_csv(MAPPING_FILE)

# ==========================================================
# CLEAN COLUMN NAMES
# ==========================================================

climate.columns = climate.columns.str.strip()
agri.columns = agri.columns.str.strip()
mapping.columns = mapping.columns.str.strip()

# ==========================================================
# STANDARDIZE DISTRICT NAMES
# ==========================================================

climate["District"] = (
    climate["District"]
    .astype(str)
    .str.strip()
    .str.upper()
)

agri["District"] = (
    agri["District"]
    .astype(str)
    .str.strip()
    .str.upper()
)

mapping["Climate_District"] = (
    mapping["Climate_District"]
    .astype(str)
    .str.strip()
    .str.upper()
)

mapping["Agriculture_District"] = (
    mapping["Agriculture_District"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# ==========================================================
# APPLY DISTRICT MAPPING
# ==========================================================

mapping_dict = dict(
    zip(
        mapping["Agriculture_District"],
        mapping["Climate_District"]
    )
)

# Handle alternate spellings
mapping_dict.update({

    "KANCHEEPURAM": "KANCHIPURAM",

    "KANCHIPURAM": "KANCHIPURAM",

    "KANYAKUMARI": "KANNIYAKUMARI",

    "KANNIYAKUMARI": "KANNIYAKUMARI",

    "TUTICORIN": "THOOTHUKUDI",

    "THOOTHUKUDI": "THOOTHUKUDI",

    "VILLUPURAM": "VILUPPURAM",

    "VILUPPURAM": "VILUPPURAM",

    "THE NILGIRIS": "NILGIRIS",

    "NILGIRIS": "NILGIRIS"

})

agri["District"] = agri["District"].replace(mapping_dict)

# ==========================================================
# YEAR FORMAT
# ==========================================================

climate["Year"] = pd.to_numeric(
    climate["Year"],
    errors="coerce"
)

agri["Year"] = pd.to_numeric(
    agri["Year"],
    errors="coerce"
)

climate = climate.dropna(subset=["Year"])
agri = agri.dropna(subset=["Year"])

climate["Year"] = climate["Year"].astype(int)
agri["Year"] = agri["Year"].astype(int)

# ==========================================================
# DATA SUMMARY
# ==========================================================

print()
print("Climate Records      :", len(climate))
print("Agriculture Records  :", len(agri))
print()

print("Climate Districts    :", climate["District"].nunique())
print("Agriculture Districts:", agri["District"].nunique())
print()

print("Climate Year Range   :",
      climate["Year"].min(),
      "-",
      climate["Year"].max())

print("Agriculture Year Range:",
      agri["Year"].min(),
      "-",
      agri["Year"].max())

# ==========================================================
# DEBUG DISTRICTS
# ==========================================================

climate_set = set(climate["District"].unique())
agri_set = set(agri["District"].unique())

print()
print("=" * 60)
print("DISTRICT CHECK")
print("=" * 60)

print()

print("Only In Climate Dataset")
only_climate = sorted(climate_set - agri_set)
print(only_climate if only_climate else "None")

print()

print("Only In Agriculture Dataset")
only_agri = sorted(agri_set - climate_set)
print(only_agri if only_agri else "None")

# ==========================================================
# MERGE
# ==========================================================

merged = pd.merge(
    agri,
    climate,
    on=["District", "Year"],
    how="inner"
)

merged = merged.sort_values(
    ["District", "Year", "Crop"]
).reset_index(drop=True)

# ==========================================================
# SAVE
# ==========================================================

merged.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================================
# SUMMARY
# ==========================================================

print()
print("=" * 60)
print("MERGE COMPLETED")
print("=" * 60)

print()

print("Merged Records :", len(merged))

if len(merged) > 0:
    print("Districts      :", merged["District"].nunique())
    print("Years          :", merged["Year"].min(), "-", merged["Year"].max())
    print("Crops          :", merged["Crop"].nunique())
else:
    print("No matching records found.")

print()

print("Columns")
for col in merged.columns:
    print("-", col)

print()
print("Saved To")
print(OUTPUT_FILE)

print()
print("=" * 60)
print("DATA INTEGRATION COMPLETED SUCCESSFULLY")
print("=" * 60)