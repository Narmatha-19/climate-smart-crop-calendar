import pandas as pd

df = pd.read_csv("../../dataset/raw/agriculture/crop_production.csv")

# Filter Tamil Nadu
df = df[df["State_Name"] == "Tamil Nadu"]

# Search for one specific record
rows = df[
    (df["District_Name"].str.upper() == "ARIYALUR") &
    (df["Crop_Year"] == 2009) &
    (df["Crop"] == "Banana")
]

print(rows)