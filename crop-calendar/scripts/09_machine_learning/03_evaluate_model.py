"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Machine Learning
Script  : 03_evaluate_random_forest.py
Purpose : Evaluate Random Forest Model
============================================================
"""

import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# ==========================================================
# PATHS
# ==========================================================

DATASET = "../../dataset/final/ml_dataset.csv"

MODEL_FILE = "../../models/random_forest_model.pkl"

OUTPUT_FOLDER = "../../output/machine_learning"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ACTUAL_PREDICTED_PLOT = os.path.join(
    OUTPUT_FOLDER,
    "actual_vs_predicted.png"
)

RESIDUAL_PLOT = os.path.join(
    OUTPUT_FOLDER,
    "residual_plot.png"
)

ERROR_DISTRIBUTION = os.path.join(
    OUTPUT_FOLDER,
    "error_distribution.png"
)

FEATURE_IMPORTANCE_PLOT = os.path.join(
    OUTPUT_FOLDER,
    "feature_importance_bar.png"
)

REPORT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "model_evaluation_report.txt"
)

# ==========================================================
# LOAD DATASET
# ==========================================================

print("=" * 60)
print("RANDOM FOREST MODEL EVALUATION")
print("=" * 60)

df = pd.read_csv(DATASET)

print("\nDataset Loaded Successfully")
print("Records :", len(df))
print("Columns :", len(df.columns))

# ==========================================================
# FEATURES
# ==========================================================

X = df.drop(columns=[
    "Yield",
    "Production",
    "Yield_Category"
])

y = df["Yield"]

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ==========================================================
# LOAD MODEL
# ==========================================================

print("\nLoading Trained Model...")

model = joblib.load(MODEL_FILE)

print("Model Loaded Successfully.")

# ==========================================================
# PREDICTIONS
# ==========================================================

train_predictions = model.predict(X_train)
test_predictions = model.predict(X_test)

# ==========================================================
# METRICS
# ==========================================================

train_r2 = r2_score(y_train, train_predictions)

test_r2 = r2_score(y_test, test_predictions)

mae = mean_absolute_error(
    y_test,
    test_predictions
)

rmse = mean_squared_error(
    y_test,
    test_predictions
) ** 0.5

# ==========================================================
# PRINT RESULTS
# ==========================================================

print("\n")
print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"Training R² : {train_r2:.4f}")
print(f"Testing R²  : {test_r2:.4f}")
print(f"MAE         : {mae:.2f}")
print(f"RMSE        : {rmse:.2f}")

# ==========================================================
# ACTUAL VS PREDICTED
# ==========================================================

plt.figure(figsize=(8,6))

plt.scatter(
    y_test,
    test_predictions,
    alpha=0.6
)

plt.plot(
    [y_test.min(), y_test.max()],
    [y_test.min(), y_test.max()],
    'r--',
    linewidth=2
)

plt.xlabel("Actual Yield")
plt.ylabel("Predicted Yield")
plt.title("Actual vs Predicted Yield")

plt.tight_layout()
plt.savefig(ACTUAL_PREDICTED_PLOT)
plt.close()

# ==========================================================
# RESIDUAL PLOT
# ==========================================================

residuals = y_test - test_predictions

plt.figure(figsize=(8,6))

plt.scatter(
    test_predictions,
    residuals,
    alpha=0.6
)

plt.axhline(
    y=0,
    color="red",
    linestyle="--"
)

plt.xlabel("Predicted Yield")
plt.ylabel("Residual")
plt.title("Residual Plot")

plt.tight_layout()
plt.savefig(RESIDUAL_PLOT)
plt.close()

# ==========================================================
# ERROR DISTRIBUTION
# ==========================================================

plt.figure(figsize=(8,6))

plt.hist(
    residuals,
    bins=30
)

plt.xlabel("Prediction Error")
plt.ylabel("Frequency")
plt.title("Error Distribution")

plt.tight_layout()
plt.savefig(ERROR_DISTRIBUTION)
plt.close()

# ==========================================================
# FEATURE IMPORTANCE BAR CHART
# ==========================================================

importance = pd.DataFrame({

    "Feature": X.columns,

    "Importance": model.feature_importances_

})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

plt.figure(figsize=(10,7))

plt.barh(
    importance["Feature"],
    importance["Importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Random Forest Feature Importance")

plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig(FEATURE_IMPORTANCE_PLOT)
plt.close()

# ==========================================================
# SAVE REPORT
# ==========================================================

with open(REPORT_FILE, "w") as file:

    file.write("="*60 + "\n")
    file.write("RANDOM FOREST MODEL EVALUATION REPORT\n")
    file.write("="*60 + "\n\n")

    file.write(f"Training R² : {train_r2:.4f}\n")
    file.write(f"Testing R²  : {test_r2:.4f}\n")
    file.write(f"MAE         : {mae:.2f}\n")
    file.write(f"RMSE        : {rmse:.2f}\n\n")

    file.write("Top 10 Important Features\n")
    file.write("-"*40 + "\n")

    for _, row in importance.head(10).iterrows():
        file.write(
            f"{row['Feature']} : {row['Importance']:.6f}\n"
        )

# ==========================================================
# SUMMARY
# ==========================================================

print("\n")
print("=" * 60)
print("EVALUATION COMPLETED")
print("=" * 60)

print("\nGenerated Files")

print("- Actual vs Predicted Plot")
print("- Residual Plot")
print("- Error Distribution")
print("- Feature Importance Plot")
print("- Evaluation Report")

print("\nSaved To")
print(OUTPUT_FOLDER)

print("\n")
print("=" * 60)
print("RANDOM FOREST EVALUATION COMPLETED SUCCESSFULLY")
print("=" * 60)