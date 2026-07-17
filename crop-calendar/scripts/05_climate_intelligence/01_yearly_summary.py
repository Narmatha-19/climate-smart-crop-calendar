import os
import pandas as pd

# ==========================================
# Folder Paths
# ==========================================

INPUT_FOLDER = "../../dataset/processed"
OUTPUT_FOLDER = "../../output/climate_intelligence"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================
# Read all cleaned datasets
# ==========================================

files = os.listdir(INPUT_FOLDER)

all_districts = []

# ==========================================
# Process each district
# ==========================================

for file in files:

    if not file.endswith(".csv"):
        continue

    district = file.replace(".csv", "")

    print(f"Processing {district}...")

    filepath = os.path.join(INPUT_FOLDER, file)

    df = pd.read_csv(filepath)

    # -----------------------------
    # Convert Date
    # -----------------------------

    df["Date"] = pd.to_datetime(df["Date"])

    df["Year"] = df["Date"].dt.year

    # -----------------------------
    # Group by Year
    # -----------------------------

    yearly = (
        df.groupby("Year")
        .agg(
            AvgTemperature=("Temperature", "mean"),
            MaxTemperature=("Temperature", "max"),
            MinTemperature=("Temperature", "min"),

            TotalRainfall=("Rainfall", "sum"),
            AvgRainfall=("Rainfall", "mean"),
            MaxRainfall=("Rainfall", "max"),

            AvgHumidity=("Humidity", "mean"),
            AvgWindSpeed=("WindSpeed", "mean"),

            RainyDays=("Rainfall", lambda x: (x > 1).sum()),

            TemperatureStd=("Temperature", "std"),
            RainfallStd=("Rainfall", "std")
        )
        .reset_index()
    )

    yearly.insert(0, "District", district)

    all_districts.append(yearly)

# ==========================================
# Merge all districts
# ==========================================

final_df = pd.concat(all_districts)

# ==========================================
# Round values
# ==========================================

final_df = final_df.round(2)

# ==========================================
# Save
# ==========================================

output_file = os.path.join(
    OUTPUT_FOLDER,
    "yearly_summary.csv"
)

final_df.to_csv(output_file, index=False)

print("\n===================================")
print("YEARLY SUMMARY CREATED")
print("===================================")
print(final_df.head())