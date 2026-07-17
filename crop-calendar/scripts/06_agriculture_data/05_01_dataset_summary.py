import os
import pandas as pd

# ==========================================
# PATHS
# ==========================================

INPUT_FILE = "../../dataset/processed/agriculture/agriculture_clean.csv"

OUTPUT_FOLDER = "../../output/agriculture/analysis"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "dataset_summary.csv"
)

# ==========================================
# READ DATA
# ==========================================

print("=" * 60)
print("AGRICULTURE DATASET SUMMARY")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# ==========================================
# CALCULATE SUMMARY
# ==========================================

summary = pd.DataFrame({

    "Metric": [

        "Total Records",
        "Total Columns",
        "Total Districts",
        "Total Crops",
        "Total Seasons",
        "Year Range",
        "Total Area",
        "Total Production",
        "Average Yield",
        "Maximum Yield",
        "Minimum Yield"

    ],

    "Value": [

        len(df),

        len(df.columns),

        df["District"].nunique(),

        df["Crop"].nunique(),

        df["Season"].nunique(),

        f"{df['Year'].min()} - {df['Year'].max()}",

        round(df["Area"].sum(), 2),

        round(df["Production"].sum(), 2),

        round(df["Yield"].mean(), 2),

        round(df["Yield"].max(), 2),

        round(df["Yield"].min(), 2)

    ]

})

# ==========================================
# SAVE
# ==========================================

summary.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================
# DISPLAY
# ==========================================

print("\n")
print(summary)

print("\n" + "=" * 60)
print("DATASET SUMMARY SAVED SUCCESSFULLY")
print("=" * 60)

print(f"\nSaved To : {OUTPUT_FILE}")