import os
import requests
import pandas as pd
from tqdm import tqdm

# ======================================================
# PROJECT PATHS
# ======================================================

# Project Root Folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input File
DISTRICT_FILE = os.path.join(
    BASE_DIR,
    "dataset",
    "raw",
    "district_coordinates.csv"
)

# Output Folder
OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "output",
    "climate_data"
)

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ======================================================
# READ DISTRICT DATA
# ======================================================

districts = pd.read_csv(DISTRICT_FILE)

# ======================================================
# NASA PARAMETERS
# ======================================================

parameters = [
    "T2M",
    "PRECTOTCORR",
    "RH2M",
    "WS2M"
]

# ======================================================
# DOWNLOAD DATA
# ======================================================

for index, row in tqdm(districts.iterrows(), total=len(districts)):

    district = row["District"]
    latitude = row["Latitude"]
    longitude = row["Longitude"]

    print(f"\nDownloading data for {district}...")

    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={','.join(parameters)}"
        f"&community=AG"
        f"&longitude={longitude}"
        f"&latitude={latitude}"
        f"&start=20050101"
        f"&end=20251231"
        f"&format=JSON"
    )

    try:
        response = requests.get(url, timeout=60)

        if response.status_code != 200:
            print(f"❌ Failed : {district}")
            continue

        data = response.json()

        parameter_data = data["properties"]["parameter"]

        df = pd.DataFrame(parameter_data)

        df.index.name = "Date"

        df.reset_index(inplace=True)

        filename = os.path.join(
            OUTPUT_FOLDER,
            f"{district}.csv"
        )

        df.to_csv(filename, index=False)

        print(f"✅ Saved : {district}.csv")

    except Exception as e:

        print(f"❌ Error downloading {district}")

        print(e)

print("\n========================================")
print(" NASA Climate Data Download Completed ")
print("========================================")