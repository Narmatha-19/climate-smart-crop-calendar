"""
============================================================
Project : Climate-Smart Crop Calendar Recommender
Module  : Machine Learning
Script  : 06_train_xgboost.py
Purpose : Train Optimized XGBoost Regression Model
============================================================
"""

import os
import joblib
import pandas as pd

from xgboost import XGBRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ==========================================================
# PATHS
# ==========================================================

DATASET = "../../dataset/final/ml_dataset.csv"

MODEL_FOLDER = "../../models"
OUTPUT_FOLDER = "../../output/machine_learning"

os.makedirs(MODEL_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

MODEL_FILE = os.path.join(MODEL_FOLDER, "xgboost_model.pkl")

FEATURE_FILE = os.path.join(OUTPUT_FOLDER, "xgboost_feature_importance.csv")

PREDICTION_FILE = os.path.join(OUTPUT_FOLDER, "xgboost_prediction_results.csv")

METRIC_FILE = os.path.join(OUTPUT_FOLDER, "xgboost_metrics.csv")

# ==========================================================
# LOAD DATASET
# ==========================================================

print("=" * 60)
print("OPTIMIZED XGBOOST MODEL TRAINING")
print("=" * 60)

df = pd.read_csv(DATASET)

print("\nDataset Loaded Successfully")
print("Records :", len(df))
print("Columns :", len(df.columns))

# ==========================================================
# FEATURES AND TARGET
# ==========================================================

# Remove target and target-related leakage features
X = df.drop(columns=["Yield", "Production", "Yield_Category"])

y = df["Yield"]

print("\nFeatures Used :", len(X.columns))
print("Target        : Yield")

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

print("\nTraining Samples :", len(X_train))
print("Testing Samples  :", len(X_test))

# ==========================================================
# OPTIMIZED XGBOOST MODEL
# ==========================================================

model = XGBRegressor(
    # Number of boosting rounds. Random Forest (02_train_random_forest.py)
    # gets 300 trees at max_depth=20 - XGBoost needs a comparable trees x
    # depth budget to be a fair comparison, not a deliberately shallow one.
    n_estimators=800,
    # max_depth=3 (the previous setting) was far more conservative than
    # every other model in this comparison and put XGBoost at an artificial
    # disadvantage. depth=6 was chosen by checking train/test R² and 5-fold
    # CV together (see the project ledger) - it's the point where test R²
    # peaks before deeper trees start just memorizing train data instead of
    # generalizing better.
    max_depth=6,
    # Lower learning rate + more rounds gives more controlled learning
    learning_rate=0.03,
    # Minimum sum of instance weights in a child
    min_child_weight=1,
    # Use only part of training data for each tree
    subsample=0.85,
    # Use only part of features for each tree
    colsample_bytree=0.85,
    # L1 regularization
    reg_alpha=0.01,
    # L2 regularization
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
    objective="reg:squarederror",
)

# ==========================================================
# TRAIN MODEL
# ==========================================================

print("\nTraining Optimized XGBoost Model...")

model.fit(X_train, y_train)

print("Training Completed.")

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

rmse = mean_squared_error(y_test, test_predictions) ** 0.5

overfitting_gap = train_r2 - test_r2

# ==========================================================
# PRINT RESULTS
# ==========================================================

print("\n")
print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"Training R²      : {train_r2:.4f}")
print(f"Testing R²       : {test_r2:.4f}")
print(f"MAE              : {mae:.2f}")
print(f"RMSE             : {rmse:.2f}")
print(f"Overfitting Gap  : {overfitting_gap:.4f}")

# ==========================================================
# MODEL ASSESSMENT
# ==========================================================

print("\n")
print("=" * 60)
print("MODEL GENERALIZATION")
print("=" * 60)

if overfitting_gap <= 0.05:

    print("Status : GOOD GENERALIZATION")
    print("The training and testing performance are close.")

elif overfitting_gap <= 0.10:

    print("Status : MODERATE OVERFITTING")
    print("The model shows some difference between training and testing.")

else:

    print("Status : HIGH OVERFITTING")
    print("The model may still be too complex.")

# ==========================================================
# SAVE MODEL
# ==========================================================

joblib.dump(model, MODEL_FILE)

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

importance = pd.DataFrame(
    {"Feature": X.columns, "Importance": model.feature_importances_}
)

importance = importance.sort_values(by="Importance", ascending=False)

importance.to_csv(FEATURE_FILE, index=False)

# ==========================================================
# SAVE PREDICTIONS
# ==========================================================

prediction_df = pd.DataFrame(
    {
        "Actual_Yield": y_test.values,
        "Predicted_Yield": test_predictions,
        "Absolute_Error": abs(y_test.values - test_predictions),
    }
)

prediction_df.to_csv(PREDICTION_FILE, index=False)

# ==========================================================
# SAVE METRICS
# ==========================================================

metrics = pd.DataFrame(
    {
        "Metric": ["Training_R2", "Testing_R2", "MAE", "RMSE", "Overfitting_Gap"],
        "Value": [train_r2, test_r2, mae, rmse, overfitting_gap],
    }
)

metrics.to_csv(METRIC_FILE, index=False)

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
print("OPTIMIZED XGBOOST TRAINING SUCCESSFUL")
print("=" * 60)
