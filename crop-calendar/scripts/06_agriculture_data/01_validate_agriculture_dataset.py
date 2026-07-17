import os
import pandas as pd

# ==========================================
# PATHS
# ==========================================

INPUT_FILE = "../../dataset/raw/agriculture/crop_production.csv"

OUTPUT_FOLDER = "../../output/agriculture"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================
# CHECK FILE
# ==========================================

if not os.path.exists(INPUT_FILE):

    print("ERROR : Dataset not found!")

    print("Expected Location:")

    print(INPUT_FILE)

    exit()

print("=" * 60)
print("AGRICULTURE DATASET VALIDATION")
print("=" * 60)

# ==========================================
# READ DATASET
# ==========================================

df = pd.read_csv(INPUT_FILE)

# ==========================================
# BASIC INFORMATION
# ==========================================

rows = len(df)

columns = len(df.columns)

print(f"\nTotal Rows      : {rows:,}")
print(f"Total Columns   : {columns}")

print("\nColumn Names:")

for column in df.columns:
    print(" -", column)

# ==========================================
# UNIQUE COUNTS
# ==========================================

states = df["State_Name"].nunique()

districts = df["District_Name"].nunique()

crops = df["Crop"].nunique()

years = df["Crop_Year"].nunique()

print("\n--------------------------------")

print(f"States          : {states}")

print(f"Districts       : {districts}")

print(f"Crops           : {crops}")

print(f"Years           : {years}")

print("--------------------------------")

# ==========================================
# YEAR RANGE
# ==========================================

print(f"\nYear Range : {df['Crop_Year'].min()} - {df['Crop_Year'].max()}")

# ==========================================
# MISSING VALUES
# ==========================================

print("\nMissing Values")

missing = df.isnull().sum()

print(missing)

# ==========================================
# DUPLICATES
# ==========================================

duplicates = df.duplicated().sum()

print(f"\nDuplicate Rows : {duplicates}")

# ==========================================
# SAVE REPORT
# ==========================================

report_file = os.path.join(

    OUTPUT_FOLDER,

    "dataset_validation_report.txt"

)

with open(report_file, "w", encoding="utf-8") as report:

    report.write("=" * 60 + "\n")

    report.write("AGRICULTURE DATASET VALIDATION REPORT\n")

    report.write("=" * 60 + "\n\n")

    report.write(f"Rows : {rows}\n")

    report.write(f"Columns : {columns}\n\n")

    report.write("COLUMN NAMES\n")

    report.write("------------------------\n")

    for column in df.columns:

        report.write(column + "\n")

    report.write("\n")

    report.write(f"States : {states}\n")

    report.write(f"Districts : {districts}\n")

    report.write(f"Crops : {crops}\n")

    report.write(f"Years : {years}\n")

    report.write(f"Year Range : {df['Crop_Year'].min()} - {df['Crop_Year'].max()}\n")

    report.write(f"Duplicate Rows : {duplicates}\n\n")

    report.write("MISSING VALUES\n")

    report.write("------------------------\n")

    report.write(missing.to_string())

print("\n")

print("=" * 60)

print("DATASET VALIDATION COMPLETED SUCCESSFULLY")

print("=" * 60)

print(f"\nReport Saved : {report_file}")