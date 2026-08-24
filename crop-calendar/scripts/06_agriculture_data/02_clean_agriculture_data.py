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
#
# Original 8 food/cash crops, plus 17 more added after checking every
# remaining Tamil Nadu crop in the raw dataset for real, usable history:
# kept the ones with >=300 records, >=15 years and >=15 districts of data
# (same order of magnitude as the original 8), covering the millets,
# pulses, oilseeds, spices and plantation crops missing from the original
# list. Crops that failed that bar were left out - not because they don't
# matter, but because the model can't learn anything reliable from them:
#   - Mango, Grapes, Papaya, Citrus Fruit: only 2 years of TN data (2002-03)
#   - Korra, Varagu, Samai, Mesta, Sannhamp: 2-3 years of TN data
#   - Potato, Garlic, Ginger, Black pepper, Cardamom: <300 records/thin district coverage
#   - Coconut: excluded separately - see the Production-unit note below
#   - Tea, Coffee, Rubber: not present in this dataset at all (tracked by
#     the Tea/Coffee/Rubber Boards separately, not the crop-census source
#     this project uses) - would need a different data source entirely.

required_crops = [

    "Rice",
    "Maize",
    "Ragi",
    "Bajra",
    "Groundnut",
    "Sugarcane",
    "Cotton(lint)",
    "Banana",

    "Urad",
    "Moong(Green Gram)",
    "Sesamum",
    "Jowar",
    "Sunflower",
    "Horse-gram",
    "Onion",
    "Arhar/Tur",
    "Dry chillies",
    "Tapioca",
    "Turmeric",
    "Cashewnut",
    "Small millets",
    "Coriander",
    "Sweet potato",
    "Gram",
    "Tobacco",

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
# FIX 100x PRODUCTION-UNIT ERROR
# ==========================================
#
# The source government dataset has a well-hidden unit bug: for every crop
# checked, many (District, Year, Season, Crop, Area) records were entered
# TWICE - once with the correct Production figure and once at exactly 100x
# that figure (confirmed on thousands of matching row-pairs before the
# dedup step above, which keeps the smaller one). The problem is that for
# a large share of records - especially 2014 onward, and a few districts
# even earlier (e.g. Thoothukudi Rice every year) - only the INFLATED
# duplicate was ever submitted, so there's no low-value partner for the
# dedup step to prefer. Left uncorrected, this produces "Yield" figures
# like 400+ tonnes/hectare for rice, which is physically impossible and
# corrupts both this dataset's reports and the ML model trained on it.
#
# Fix: for each crop, the correct value scale is well established by the
# thousands of confirmed same-scale duplicate pairs above (verified
# 90-110x apart, i.e. genuinely a ~100x pair, not just two different
# harvests). YIELD_CEILING below is 1.5x the 99th percentile of those
# confirmed-correct pairs per crop - a generous ceiling that sits well
# above every real observed value but well below the ~100x-inflated ones.
# Any record whose Production/Area exceeds that ceiling is assumed to be
# one of the orphaned duplicates and is divided by 100. Coconut was left
# out of `required_crops` above because its duplicate pairs differ by
# ~100,000x, not ~100x - a different, messier problem that this fix isn't
# designed for and that needs its own investigation before Coconut can be
# added safely.

print("\nChecking Production-Unit (100x) Errors...")

YIELD_CEILING = {
    "Rice": 8.5, "Maize": 12.87, "Ragi": 6.16, "Bajra": 5.96,
    "Groundnut": 8.47, "Sugarcane": 317.02, "Cotton(lint)": 6.78, "Banana": 118.7,
    "Urad": 1.56, "Moong(Green Gram)": 1.5, "Sesamum": 1.27, "Jowar": 4.87,
    "Sunflower": 3.92, "Horse-gram": 1.5, "Onion": 25.09, "Arhar/Tur": 2.21,
    "Dry chillies": 2.55, "Tapioca": 89.08, "Turmeric": 12.91, "Cashewnut": 1.62,
    "Small millets": 18.66, "Coriander": 1.25, "Sweet potato": 45.2,
    "Gram": 1.81, "Tobacco": 7.2,
}

df["Yield"] = df["Production"] / df["Area"]
ceiling = df["Crop"].map(YIELD_CEILING)

inflated = df["Yield"] > ceiling
print("Records Rescaled (÷100)   :", int(inflated.sum()))

df.loc[inflated, "Production"] = df.loc[inflated, "Production"] / 100
df["Yield"] = df["Production"] / df["Area"]

# Safety net: a handful of records are broken in a way ÷100 can't fix
# (e.g. one Cashewnut/Perambalur/2008 row has Area recorded as 1.0 hectare,
# clearly wrong regardless of the Production unit). Anything still >3x its
# ceiling after the rescale above is dropped rather than guessed at further.
unfixable = df["Yield"] > (ceiling * 3)
print("Unfixable Records Dropped :", int(unfixable.sum()))
df = df[~unfixable]

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