"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Machine Learning
Script  : 02_train_random_forest.py
Purpose : Train Random Forest Regression Model
============================================================
"""

import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
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

MODEL_FOLDER = "../../models"

OUTPUT_FOLDER = "../../output/machine_learning"

os.makedirs(MODEL_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

MODEL_FILE = os.path.join(
    MODEL_FOLDER,
    "random_forest_model.pkl"
)

FEATURE_FILE = os.path.join(
    OUTPUT_FOLDER,
    "feature_importance.csv"
)

PREDICTION_FILE = os.path.join(
    OUTPUT_FOLDER,
    "prediction_results.csv"
)

METRIC_FILE = os.path.join(
    OUTPUT_FOLDER,
    "model_metrics.csv"
)

# ==========================================================
# LOAD DATASET
# ==========================================================

print("=" * 60)
print("RANDOM FOREST MODEL TRAINING")
print("=" * 60)

df = pd.read_csv(DATASET)

print("\nDataset Loaded Successfully")
print("Records :", len(df))
print("Columns :", len(df.columns))

# ==========================================================
# FEATURES & TARGET
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

print("\nTraining Samples :", len(X_train))
print("Testing Samples  :", len(X_test))

# ==========================================================
# RANDOM FOREST MODEL
# ==========================================================

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

print("\nTraining Model...")

model.fit(X_train, y_train)

print("Training Completed.")

# ==========================================================
# PREDICTIONS
# ==========================================================

train_prediction = model.predict(X_train)
test_prediction = model.predict(X_test)

# ==========================================================
# METRICS
# ==========================================================

train_r2 = r2_score(
    y_train,
    train_prediction
)

test_r2 = r2_score(
    y_test,
    test_prediction
)

mae = mean_absolute_error(
    y_test,
    test_prediction
)

rmse = mean_squared_error(
    y_test,
    test_prediction
) ** 0.5

# ==========================================================
# RESULTS
# ==========================================================

print("\n")
print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"Training R² : {train_r2:.4f}")
print(f"Testing R²  : {test_r2:.4f}")
print(f"MAE          : {mae:.2f}")
print(f"RMSE         : {rmse:.2f}")

# ==========================================================
# SAVE MODEL
# ==========================================================

joblib.dump(
    model,
    MODEL_FILE
)

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

importance.to_csv(
    FEATURE_FILE,
    index=False
)

# ==========================================================
# SAVE PREDICTIONS
# ==========================================================

prediction_df = pd.DataFrame({

    "Actual_Yield": y_test.values,

    "Predicted_Yield": test_prediction,

    "Absolute_Error": abs(
        y_test.values - test_prediction
    )

})

prediction_df.to_csv(
    PREDICTION_FILE,
    index=False
)

# ==========================================================
# SAVE METRICS
# ==========================================================

metrics = pd.DataFrame({

    "Metric": [

        "Training_R2",
        "Testing_R2",
        "MAE",
        "RMSE"

    ],

    "Value": [

        train_r2,
        test_r2,
        mae,
        rmse

    ]

})

metrics.to_csv(
    METRIC_FILE,
    index=False
)

# ==========================================================
# SUMMARY
# ==========================================================

print("\n")
print("=" * 60)
print("MODEL TRAINING COMPLETED")
print("=" * 60)

print("\nModel Saved")
print(MODEL_FILE)

print("\nFeature Importance Saved")
print(FEATURE_FILE)

print("\nPrediction Results Saved")
print(PREDICTION_FILE)

print("\nMetrics Saved")
print(METRIC_FILE)

print("\n")
print("=" * 60)
print("RANDOM FOREST TRAINING SUCCESSFUL")
print("=" * 60)