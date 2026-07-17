import pandas as pd
import os

# Read district files from output folder
input_folder = "../output/climate_data"

# Create processed_data folder if it doesn't exist
os.makedirs("../dataset/processed_data", exist_ok=True)

# Save merged dataset here
output_file = "../dataset/processed_data/master_climate_dataset.csv"

all_data = []

for file in os.listdir(input_folder):

    if file.endswith(".csv"):

        district = file.replace(".csv", "")

        filepath = os.path.join(input_folder, file)

        df = pd.read_csv(filepath)

        df["District"] = district

        all_data.append(df)

master_df = pd.concat(all_data, ignore_index=True)

master_df.to_csv(output_file, index=False)

print("Dataset merged successfully!")
print(master_df.head())