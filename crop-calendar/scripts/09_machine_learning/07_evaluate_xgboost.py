"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Machine Learning
Script  : 07_evaluate_xgboost.py
Purpose : Evaluate XGBoost Regression Model
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

MODEL_FILE = "../../models/xgboost_model.pkl"

OUTPUT_FOLDER = "../../output/machine_learning"

FEATURE_FILE = os.path.join(
    OUTPUT_FOLDER,
    "xgboost_feature_importance.csv"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# LOAD DATASET
# ==========================================================

print("=" * 60)
print("XGBOOST MODEL EVALUATION")
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

mae = mean_absolute_error(y_test, test_predictions)

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
    'r--'
)

plt.xlabel("Actual Yield")
plt.ylabel("Predicted Yield")
plt.title("XGBoost - Actual vs Predicted")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "xgboost_actual_vs_predicted.png"
    )
)

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
    color='red',
    linestyle='--'
)

plt.xlabel("Predicted Yield")
plt.ylabel("Residual")

plt.title("XGBoost Residual Plot")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "xgboost_residual_plot.png"
    )
)

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

plt.title("XGBoost Error Distribution")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "xgboost_error_distribution.png"
    )
)

plt.close()

# ==========================================================
# FEATURE IMPORTANCE BAR
# ==========================================================

importance = pd.read_csv(FEATURE_FILE)

plt.figure(figsize=(10,8))

plt.barh(
    importance["Feature"],
    importance["Importance"]
)

plt.title("XGBoost Feature Importance")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_FOLDER,
        "xgboost_feature_importance_bar.png"
    )
)

plt.close()

# ==========================================================
# REPORT
# ==========================================================

report = os.path.join(
    OUTPUT_FOLDER,
    "xgboost_evaluation_report.txt"
)

with open(report, "w") as f:

    f.write("="*60 + "\n")
    f.write("XGBOOST MODEL EVALUATION REPORT\n")
    f.write("="*60 + "\n\n")

    f.write(f"Training R² : {train_r2:.4f}\n")
    f.write(f"Testing R²  : {test_r2:.4f}\n")
    f.write(f"MAE         : {mae:.2f}\n")
    f.write(f"RMSE        : {rmse:.2f}\n")

# ==========================================================
# SUMMARY
# ==========================================================

print("\n")
print("=" * 60)
print("EVALUATION COMPLETED")
print("=" * 60)

print("\nGenerated Files")

print("- XGBoost Actual vs Predicted Plot")
print("- XGBoost Residual Plot")
print("- XGBoost Error Distribution")
print("- XGBoost Feature Importance Plot")
print("- XGBoost Evaluation Report")

print("\nSaved To")

print(OUTPUT_FOLDER)

print("\n")
print("=" * 60)
print("XGBOOST EVALUATION COMPLETED SUCCESSFULLY")
print("=" * 60)