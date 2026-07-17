"""
Machine Learning Prediction Pipeline
=====================================
This module currently ships with a deterministic, rule-based PLACEHOLDER
so the full application is runnable end-to-end without a trained model
or live weather API.

To go to production, replace `predict_crop_recommendation()` internals
with a real pipeline, e.g.:

    import joblib
    import pandas as pd
    import numpy as np
    from xgboost import XGBRegressor          # sowing-window regression
    from sklearn.ensemble import RandomForestClassifier  # risk classification

    xgb_model = joblib.load("models/trained/sowing_window_xgb.pkl")
    risk_model = joblib.load("models/trained/risk_classifier.pkl")

The five-step AI process flow described in the product brief is kept as
five explicit functions below so each stage can be independently swapped
for a real implementation (live weather API calls, monsoon anomaly
detection, XGBoost inference, etc.) without touching app.py.
"""

import random
from datetime import datetime, timedelta

# Base climate profiles per district (placeholder "historical averages").
# Replace with real IMD / data.gov.in climate normals when wiring a live source.
DISTRICT_CLIMATE_PROFILE = {
    "Chennai":      {"base_rainfall": 140, "base_temp": 32, "base_humidity": 72, "base_wind": 14},
    "Thanjavur":    {"base_rainfall": 190, "base_temp": 31, "base_humidity": 78, "base_wind": 12},
    "Madurai":      {"base_rainfall": 110, "base_temp": 33, "base_humidity": 65, "base_wind": 13},
    "Coimbatore":   {"base_rainfall": 95,  "base_temp": 29, "base_humidity": 68, "base_wind": 11},
    "Trichy":       {"base_rainfall": 120, "base_temp": 33, "base_humidity": 66, "base_wind": 12},
    "Salem":        {"base_rainfall": 105, "base_temp": 30, "base_humidity": 64, "base_wind": 10},
    "Tirunelveli":  {"base_rainfall": 130, "base_temp": 32, "base_humidity": 70, "base_wind": 15},
    "Erode":        {"base_rainfall": 90,  "base_temp": 31, "base_humidity": 63, "base_wind": 11},
}

# Ideal sowing windows per (crop, season) — placeholder agronomic calendar.
SOWING_CALENDAR = {
    ("Rice", "Kuruvai"):     {"start_offset": 0,  "length_days": 6, "month": 6, "day": 24},
    ("Rice", "Samba"):       {"start_offset": 0,  "length_days": 10, "month": 8, "day": 10},
    ("Rice", "Navarai"):     {"start_offset": 0,  "length_days": 7,  "month": 1, "day": 15},
    ("Groundnut", "Kuruvai"):{"start_offset": 0,  "length_days": 8,  "month": 6, "day": 15},
    ("Cotton", "Kuruvai"):   {"start_offset": 0,  "length_days": 9,  "month": 7, "day": 1},
    ("Sugarcane", "Samba"):  {"start_offset": 0,  "length_days": 12, "month": 1, "day": 20},
    ("Maize", "Navarai"):    {"start_offset": 0,  "length_days": 6,  "month": 2, "day": 5},
    ("Millets", "Kuruvai"):  {"start_offset": 0,  "length_days": 7,  "month": 6, "day": 20},
    ("Banana", "Samba"):     {"start_offset": 0,  "length_days": 14, "month": 8, "day": 1},
}


def _seed(district, crop, season):
    """Deterministic seed so the same inputs always return the same output."""
    return abs(hash((district, crop, season))) % (10 ** 6)


def retrieve_climate_data(district):
    """Step 1: Climate Data Retrieval (placeholder for live weather API)."""
    profile = DISTRICT_CLIMATE_PROFILE.get(district, DISTRICT_CLIMATE_PROFILE["Thanjavur"])
    return profile


def detect_monsoon_shift(district, seed):
    """Step 2: Monsoon Shift Detection (placeholder anomaly detector)."""
    rng = random.Random(seed)
    shift_days = rng.choice([-5, -3, 0, 0, 2, 4, 7])
    return shift_days


def analyze_rainfall(profile, shift_days, seed):
    """Step 3: Rainfall Analysis."""
    rng = random.Random(seed + 1)
    variability = rng.uniform(-0.15, 0.15)
    expected_rainfall = round(profile["base_rainfall"] * (1 + variability), 1)
    return expected_rainfall


def assess_climate_risk(expected_rainfall, profile, shift_days, seed):
    """Step 4: Climate Risk Assessment."""
    rng = random.Random(seed + 2)

    if expected_rainfall < profile["base_rainfall"] * 0.75:
        drought_risk = "High"
    elif expected_rainfall < profile["base_rainfall"] * 0.9:
        drought_risk = "Moderate"
    else:
        drought_risk = "Low"

    if expected_rainfall > profile["base_rainfall"] * 1.2 or shift_days >= 5:
        flood_risk = "High"
    elif expected_rainfall > profile["base_rainfall"] * 1.05 or shift_days >= 2:
        flood_risk = "Moderate"
    else:
        flood_risk = "Low"

    risk_rank = {"Low": 0, "Moderate": 1, "High": 2}
    overall_rank = max(risk_rank[drought_risk], risk_rank[flood_risk])
    overall_risk = {0: "Low", 1: "Moderate", 2: "High"}[overall_rank]

    stability_score = round(100 - (overall_rank * 25) - rng.uniform(0, 8), 1)
    return drought_risk, flood_risk, overall_risk, stability_score


def ml_predict_sowing_window(crop, season, shift_days, overall_risk, seed):
    """
    Step 5: Machine Learning Prediction (placeholder).

    In production this becomes a call to a trained XGBoost regressor that
    predicts the optimal sowing start date offset (in days) based on
    engineered features: rainfall anomaly, soil moisture index, monsoon
    onset date, NDVI trend, and historical yield response curves.
    """
    calendar_entry = SOWING_CALENDAR.get(
        (crop, season),
        {"start_offset": 0, "length_days": 7, "month": 6, "day": 20},
    )

    today = datetime.now()
    year = today.year if today.month <= calendar_entry["month"] else today.year + 1
    base_start = datetime(year, calendar_entry["month"], calendar_entry["day"])
    adjusted_start = base_start + timedelta(days=shift_days)
    window_end = adjusted_start + timedelta(days=calendar_entry["length_days"])

    rng = random.Random(seed + 3)
    best_day_offset = rng.randint(1, max(1, calendar_entry["length_days"] - 1))
    best_sowing_date = adjusted_start + timedelta(days=best_day_offset)

    base_confidence = 92
    risk_penalty = {"Low": 0, "Moderate": 8, "High": 18}[overall_risk]
    confidence_score = max(55, base_confidence - risk_penalty + rng.randint(-3, 3))

    return {
        "sowing_window": f"{adjusted_start.strftime('%d %b %Y')} \u2013 {window_end.strftime('%d %b %Y')}",
        "best_sowing_date": best_sowing_date.strftime("%d %b %Y"),
        "confidence_score": confidence_score,
    }


def generate_suggestions(crop, overall_risk, drought_risk, flood_risk, best_sowing_date):
    suggestions = [f"Prepare nursery/land at least 5 days before {best_sowing_date}."]

    if flood_risk in ("Moderate", "High"):
        suggestions.append("Keep drainage channels ready before sowing.")
        suggestions.append("Monitor rainfall alerts closely over the next 7 days.")
    if drought_risk in ("Moderate", "High"):
        suggestions.append("Plan supplemental irrigation in case of a dry spell.")
    if overall_risk == "High":
        suggestions.append("Consider a short-duration crop variety to reduce exposure.")
    else:
        suggestions.append("Avoid sowing outside the recommended window to maximize yield.")

    return suggestions[:4]


def predict_crop_recommendation(district, crop, season):
    """
    Orchestrates the full 5-step AI process flow described in the product
    brief and returns a complete recommendation payload.
    """
    seed = _seed(district, crop, season)

    profile = retrieve_climate_data(district)                                   # Step 1
    shift_days = detect_monsoon_shift(district, seed)                           # Step 2
    expected_rainfall = analyze_rainfall(profile, shift_days, seed)             # Step 3
    drought_risk, flood_risk, overall_risk, stability_score = assess_climate_risk(  # Step 4
        expected_rainfall, profile, shift_days, seed
    )
    ml_result = ml_predict_sowing_window(crop, season, shift_days, overall_risk, seed)  # Step 5

    rng = random.Random(seed + 4)
    avg_temperature = round(profile["base_temp"] + rng.uniform(-1.5, 1.5), 1)
    humidity = round(profile["base_humidity"] + rng.uniform(-5, 5), 1)
    wind_speed = round(profile["base_wind"] + rng.uniform(-2, 2), 1)

    suggestions = generate_suggestions(
        crop, overall_risk, drought_risk, flood_risk, ml_result["best_sowing_date"]
    )

    return {
        "district": district,
        "crop": crop,
        "season": season,
        "sowing_window": ml_result["sowing_window"],
        "best_sowing_date": ml_result["best_sowing_date"],
        "expected_rainfall": expected_rainfall,
        "avg_temperature": avg_temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "drought_risk": drought_risk,
        "flood_risk": flood_risk,
        "overall_risk": overall_risk,
        "climate_stability_score": stability_score,
        "confidence_score": ml_result["confidence_score"],
        "suggestions": suggestions,
    }
