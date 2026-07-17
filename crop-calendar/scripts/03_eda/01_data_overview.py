import os
import pandas as pd

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INPUT_FOLDER = os.path.join(BASE_DIR, "dataset", "processed")

SUMMARY_FOLDER = os.path.join(BASE_DIR, "output", "analysis", "summary")
TABLE_FOLDER = os.path.join(BASE_DIR, "output", "analysis", "tables")
PROFILE_FOLDER = os.path.join(BASE_DIR, "output", "analysis", "district_profiles")

os.makedirs(SUMMARY_FOLDER, exist_ok=True)
os.makedirs(TABLE_FOLDER, exist_ok=True)
os.makedirs(PROFILE_FOLDER, exist_ok=True)

# =====================================================
# VARIABLES
# =====================================================

district_statistics = []
all_data = []

# =====================================================
# READ ALL DISTRICTS
# =====================================================

for file in os.listdir(INPUT_FOLDER):

    if not file.endswith(".csv"):
        continue

    filepath = os.path.join(INPUT_FOLDER, file)

    df = pd.read_csv(filepath)

    district = file.replace(".csv", "")

    df["District"] = district

    all_data.append(df)

    stats = {

        "District": district,

        "Records": len(df),

        "Start Date": df["Date"].min(),

        "End Date": df["Date"].max(),

        "Average Temperature": round(df["Temperature"].mean(),2),

        "Minimum Temperature": round(df["Temperature"].min(),2),

        "Maximum Temperature": round(df["Temperature"].max(),2),

        "Average Rainfall": round(df["Rainfall"].mean(),2),

        "Maximum Rainfall": round(df["Rainfall"].max(),2),

        "Average Humidity": round(df["Humidity"].mean(),2),

        "Average WindSpeed": round(df["WindSpeed"].mean(),2)

    }

    district_statistics.append(stats)

    pd.DataFrame([stats]).to_csv(
        os.path.join(PROFILE_FOLDER, district + "_Profile.csv"),
        index=False
    )

# =====================================================
# MERGE ALL DISTRICTS
# =====================================================

combined = pd.concat(all_data, ignore_index=True)

# =====================================================
# DATASET SUMMARY
# =====================================================

summary = {

    "Total Districts":[combined["District"].nunique()],

    "Total Records":[len(combined)],

    "Start Date":[combined["Date"].min()],

    "End Date":[combined["Date"].max()],

    "Average Temperature":[round(combined["Temperature"].mean(),2)],

    "Average Rainfall":[round(combined["Rainfall"].mean(),2)],

    "Average Humidity":[round(combined["Humidity"].mean(),2)],

    "Average WindSpeed":[round(combined["WindSpeed"].mean(),2)],

    "Missing Values":[combined.isnull().sum().sum()],

    "Duplicate Rows":[combined.duplicated().sum()]

}

summary_df = pd.DataFrame(summary)

summary_df.to_csv(
    os.path.join(SUMMARY_FOLDER,"dataset_summary.csv"),
    index=False
)

district_df = pd.DataFrame(district_statistics)

district_df.to_csv(
    os.path.join(TABLE_FOLDER,"district_statistics.csv"),
    index=False
)

# =====================================================
# TEXT REPORT
# =====================================================

report_path = os.path.join(SUMMARY_FOLDER,"climate_summary.txt")

with open(report_path,"w") as f:

    f.write("CLIMATE SMART CROP CALENDAR\n")
    f.write("="*45+"\n\n")

    for col in summary_df.columns:

        f.write(f"{col} : {summary_df.iloc[0][col]}\n")

print("\n=====================================")
print("DATA OVERVIEW COMPLETED")
print("=====================================")

print("\nDataset Summary Saved")

print("District Statistics Saved")

print("District Profiles Saved")

print("Climate Summary Saved")