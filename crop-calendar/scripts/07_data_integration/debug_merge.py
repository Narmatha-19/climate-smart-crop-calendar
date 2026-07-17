import pandas as pd

climate = pd.read_csv("../../output/climate_intelligence/yearly_summary.csv")

agri = pd.read_csv("../../dataset/processed/agriculture/agriculture_clean.csv")

mapping = pd.read_csv("../../dataset/final/district_mapping.csv")

print("="*50)
print("Agriculture Districts")
print("="*50)
print(agri["District"].unique()[:10])

print()

print("="*50)
print("Mapping Agriculture Districts")
print("="*50)
print(mapping["Agriculture_District"].unique()[:10])

print()

print("="*50)
print("Climate Districts")
print("="*50)
print(climate["District"].unique()[:10])