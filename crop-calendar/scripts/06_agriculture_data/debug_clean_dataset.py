import pandas as pd

df = pd.read_csv("../../dataset/processed/agriculture/agriculture_clean.csv")

rows = df[
    (df["District"].str.upper() == "ARIYALUR") &
    (df["Year"] == 2009) &
    (df["Crop"] == "Banana")
]

print(rows)

# ---------------------------------------------
import pandas as pd

df = pd.read_csv("../../dataset/processed/agriculture/agriculture_clean.csv")

duplicates = df[
    (df["District"]=="ARIYALUR") &
    (df["Year"]==2009) &
    (df["Crop"]=="Banana")
]

print("Number of matching rows:", len(duplicates))
print(duplicates)

print("-------------------------------------------------")

import pandas as pd

df = pd.read_csv("../../dataset/processed/agriculture/agriculture_clean.csv")

duplicates = df.duplicated(
    subset=[
        "State",
        "District",
        "Year",
        "Season",
        "Crop",
        "Area"
    ],
    keep=False
)

print("Duplicate rows:", duplicates.sum())

if duplicates.sum() > 0:
    print(df[duplicates])
else:
    print("✅ No duplicate crop records found.")