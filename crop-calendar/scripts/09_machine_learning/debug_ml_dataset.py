import pandas as pd

df = pd.read_csv("../../dataset/final/ml_dataset.csv")

print(df.columns.tolist())
print()
print(df.head())