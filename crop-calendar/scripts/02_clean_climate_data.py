import os
import pandas as pd

# =====================================================
# PROJECT PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FOLDER = os.path.join(
    BASE_DIR,
    "output",
    "climate_data"
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "dataset",
    "processed"
)

REPORT_FOLDER = os.path.join(
    BASE_DIR,
    "output",
    "reports"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# =====================================================
# QUALITY REPORT
# =====================================================

quality_report = []

# =====================================================
# PROCESS EVERY DISTRICT
# =====================================================

for file in os.listdir(INPUT_FOLDER):

    if not file.endswith(".csv"):
        continue

    print(f"\nProcessing {file}")

    filepath = os.path.join(INPUT_FOLDER, file)

    df = pd.read_csv(filepath)

    district = file.replace(".csv", "")

    # =====================================================
    # Rename Columns
    # =====================================================

    df.rename(columns={
        "T2M": "Temperature",
        "PRECTOTCORR": "Rainfall",
        "RH2M": "Humidity",
        "WS2M": "WindSpeed"
    }, inplace=True)

    # =====================================================
    # Convert Date
    # =====================================================

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%Y%m%d"
    )

    # =====================================================
    # Missing Values
    # =====================================================

    missing_values = df.isnull().sum().sum()

    # =====================================================
    # Duplicate Rows
    # =====================================================

    duplicate_rows = df.duplicated().sum()

    df.drop_duplicates(inplace=True)

    # =====================================================
    # Invalid Climate Values
    # =====================================================

    invalid_temperature = (
        (df["Temperature"] < -20) |
        (df["Temperature"] > 60)
    ).sum()

    invalid_rainfall = (
        df["Rainfall"] < 0
    ).sum()

    invalid_humidity = (
        (df["Humidity"] < 0) |
        (df["Humidity"] > 100)
    ).sum()

    invalid_windspeed = (
        df["WindSpeed"] < 0
    ).sum()

    # =====================================================
    # Sort Data
    # =====================================================

    df.sort_values("Date", inplace=True)

    # =====================================================
    # Save Clean File
    # =====================================================

    output_path = os.path.join(
        OUTPUT_FOLDER,
        file
    )

    df.to_csv(output_path, index=False)

    # =====================================================
    # Save Report Information
    # =====================================================

    quality_report.append({

        "District": district,

        "Rows": len(df),

        "Missing Values": missing_values,

        "Duplicate Rows": duplicate_rows,

        "Invalid Temperature": invalid_temperature,

        "Invalid Rainfall": invalid_rainfall,

        "Invalid Humidity": invalid_humidity,

        "Invalid WindSpeed": invalid_windspeed,

        "Start Date": df["Date"].min().date(),

        "End Date": df["Date"].max().date(),

        "Minimum Temperature": round(df["Temperature"].min(),2),

        "Maximum Temperature": round(df["Temperature"].max(),2),

        "Maximum Rainfall": round(df["Rainfall"].max(),2),

        "Status": "PASS"

    })

# =====================================================
# SAVE REPORT
# =====================================================

report_df = pd.DataFrame(quality_report)

report_path = os.path.join(
    REPORT_FOLDER,
    "data_quality_report.csv"
)

report_df.to_csv(
    report_path,
    index=False
)

print("\n====================================")
print(" Climate Data Cleaning Completed ")
print("====================================")

print(f"\nProcessed Files Saved To : {OUTPUT_FOLDER}")

print(f"Quality Report Saved To : {report_path}")