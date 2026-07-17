import os
import pandas as pd

# ==========================================
# PATHS
# ==========================================

INPUT_FILE = "../../dataset/raw/agriculture/crop_production.csv"

OUTPUT_FOLDER = "../../dataset/processed/agriculture"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "agriculture_clean.csv"
)

# ==========================================
# READ DATASET
# ==========================================

print("=" * 60)
print("CLEANING AGRICULTURE DATASET")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(f"\nOriginal Records : {len(df):,}")

# ==========================================
# KEEP ONLY TAMIL NADU
# ==========================================

df = df[df["State_Name"] == "Tamil Nadu"].copy()

print(f"After Tamil Nadu Filter : {len(df):,}")

# ==========================================
# REQUIRED CROPS
# ==========================================

required_crops = [

    "Rice",

    "Maize",

    "Ragi",

    "Bajra",

    "Groundnut",

    "Sugarcane",

    "Cotton(lint)",

    "Banana"

]

df = df[df["Crop"].isin(required_crops)]

print(f"After Crop Filter : {len(df):,}")

# ==========================================
# RENAME COLUMNS
# ==========================================

df.rename(columns={

    "State_Name":"State",

    "District_Name":"District",

    "Crop_Year":"Year",

    "yield":"Yield"

}, inplace=True)

# ==========================================
# REMOVE SPACES
# ==========================================

df["District"] = df["District"].str.strip()

df["Crop"] = df["Crop"].str.strip()

df["Season"] = df["Season"].str.strip()

# ==========================================
# REMOVE DUPLICATE RECORDS
# ==========================================

print("\nChecking Duplicate Crop Records...")

before = len(df)

# Sort so that smaller Production is kept
df = df.sort_values(
    by=["Production"],
    ascending=True
)

# Remove duplicate records
df = df.drop_duplicates(

    subset=[
        "State",
        "District",
        "Year",
        "Season",
        "Crop",
        "Area"
    ],

    keep="first"

)

after = len(df)

print("Duplicate Records Removed :", before - after)

print("Remaining Records         :", after)

# ==========================================
# SORT
# ==========================================

df = df.sort_values(

    ["District","Year","Crop"]

)

# ==========================================
# RESET INDEX
# ==========================================

df.reset_index(

    drop=True,

    inplace=True

)

# ==========================================
# SAVE
# ==========================================

df.to_csv(

    OUTPUT_FILE,

    index=False

)

# ==========================================
# SUMMARY
# ==========================================

print("\n")

print("=" * 60)

print("CLEANING COMPLETED")

print("=" * 60)

print(f"Final Records : {len(df):,}")

print(f"Districts : {df['District'].nunique()}")

print(f"Crops : {df['Crop'].nunique()}")

print(f"Years : {df['Year'].min()} - {df['Year'].max()}")

print("\nSaved To")

print(OUTPUT_FILE)