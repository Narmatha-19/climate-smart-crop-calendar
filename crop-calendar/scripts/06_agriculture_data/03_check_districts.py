import pandas as pd

# ==========================================
# READ DATA
# ==========================================

df = pd.read_csv("../../dataset/processed/agriculture/agriculture_clean.csv")

print("=" * 60)
print("TAMIL NADU DISTRICTS")
print("=" * 60)

districts = sorted(df["District"].unique())

for i, district in enumerate(districts, start=1):
    print(f"{i:02d}. {district}")

print("\n")

print("=" * 60)
print(f"TOTAL DISTRICTS : {len(districts)}")
print("=" * 60)