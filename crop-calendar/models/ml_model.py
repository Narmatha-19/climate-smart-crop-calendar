"""
Machine Learning Prediction Pipeline
=====================================
Loads the trained XGBoost yield model (models/xgboost_model.pkl, 97.0% test
R^2 - the best of the three models compared in scripts/09_machine_learning/,
see output/machine_learning/model_comparison.csv) plus the real historical
climate/agriculture dataset and produces
data-backed crop recommendations.

The model was trained to predict Yield (tonnes/hectare) — there is no
sowing-date ground truth anywhere in the project, so the sowing window comes from the
TNAU-style reference calendar below (SOWING_CALENDAR), while the yield
prediction and the real 21-year rainfall trend
(output/climate_intelligence/reports/rainfall_trends.csv) drive the risk
assessment and confidence score. See the project plan / README for the
full reasoning behind these choices.

The five-step AI process flow from the product brief is kept as five
explicit functions so each stage stays independently readable:
  1. retrieve_climate_data   - historical climate/agriculture averages
  2. predict_yield           - real XGBoost inference
  3. assess_climate_risk     - drought/flood risk from real data
  4. get_sowing_window       - TNAU-style reference calendar
  5. build_confidence        - data-driven confidence score
"""

import os
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATASET_DIR = os.path.join(BASE_DIR, "dataset", "final")
CLIMATE_INTEL_DIR = os.path.join(BASE_DIR, "output", "climate_intelligence")
REPORTS_DIR = os.path.join(CLIMATE_INTEL_DIR, "reports")

# --------------------------------------------------------------------------
# Load trained artifacts (once, at import time)
# --------------------------------------------------------------------------
_model = joblib.load(os.path.join(MODELS_DIR, "xgboost_model.pkl"))

_ENCODED_COLUMNS = [
    "District", "Crop", "Season",
    "Temperature_Category", "Rainfall_Category",
    "Humidity_Category", "Wind_Category",
]
_encoders = {
    col: joblib.load(os.path.join(MODELS_DIR, f"{col}_encoder.pkl"))
    for col in _ENCODED_COLUMNS
}

_features_df = pd.read_csv(os.path.join(DATASET_DIR, "climate_agriculture_features.csv"))
_rainfall_trends = pd.read_csv(os.path.join(REPORTS_DIR, "rainfall_trends.csv")).set_index("District")
_temperature_trends = pd.read_csv(os.path.join(REPORTS_DIR, "temperature_trends.csv")).set_index("District")
# Real year-by-year climate averages per district, 2005-2025 — the same
# source the trend reports above were computed from (scripts/05_climate_intelligence).
_yearly_summary = pd.read_csv(os.path.join(CLIMATE_INTEL_DIR, "yearly_summary.csv"))

# Per-crop yield quantiles, not one global split - see the matching comment
# in scripts/07_data_integration/03_feature_engineering.py. Crops with very
# different natural yield scales (Sesame ~0.5 t/ha vs Sugarcane ~100 t/ha)
# would otherwise make "High/Medium/Low" mean "which crop is this" instead
# of "how did this perform relative to its own normal range". Grouped from
# _features_df (plain-string Crop column) rather than the label-encoded
# _ml_df, since predict_yield() below always has the crop name in hand.
_YIELD_QUANTILES = {
    crop: (group.quantile(0.33), group.quantile(0.66))
    for crop, group in _features_df.groupby("Crop")["Yield"]
}

# Exact column order the model was trained on:
# X = df.drop(columns=["Yield", "Production", "Yield_Category"])
FEATURE_COLUMNS = [
    "District", "Year", "Season", "Crop", "Area",
    "AvgTemperature", "MaxTemperature", "MinTemperature",
    "TotalRainfall", "AvgRainfall", "MaxRainfall",
    "AvgHumidity", "AvgWindSpeed", "RainyDays",
    "TemperatureStd", "RainfallStd",
    "Temperature_Category", "Rainfall_Category",
    "Humidity_Category", "Wind_Category",
]

_NUMERIC_HISTORY_COLUMNS = [
    "Area", "AvgTemperature", "MaxTemperature", "MinTemperature",
    "TotalRainfall", "AvgRainfall", "MaxRainfall",
    "AvgHumidity", "AvgWindSpeed", "RainyDays",
    "TemperatureStd", "RainfallStd",
]

# --------------------------------------------------------------------------
# District names: the app shows all 38 real Tamil Nadu districts, but the
# training dataset only has agricultural history under 33 names (some
# spelled differently, some newer districts folded into their parent).
# This mirrors the exact normalization used when the training dataset was
# built (scripts/07_data_integration/01_merge_climate_agriculture.py) so
# lookups always land on a district the encoders/model actually know.
# --------------------------------------------------------------------------
TN_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram",
    "Kanniyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivagangai", "Tenkasi",
    "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
    "Vellore", "Viluppuram", "Virudhunagar",
]

# Original 8 crops, plus 17 more (see scripts/06_agriculture_data/02_clean_agriculture_data.py
# for exactly which TN crops were checked and why these 17 made the cut - short version:
# real TN cultivation history with >=300 records, >=15 years, >=15 districts).
# Excludes Coconut (production-unit data too broken to safely correct in this
# pass) and Tea/Coffee/Rubber (not present in this dataset's source at all).
CROPS = [
    "Rice", "Groundnut", "Cotton(lint)", "Sugarcane", "Maize", "Bajra", "Ragi", "Banana",
    "Urad", "Moong(Green Gram)", "Sesamum", "Jowar", "Sunflower", "Horse-gram", "Onion",
    "Arhar/Tur", "Dry chillies", "Tapioca", "Turmeric", "Cashewnut", "Small millets",
    "Coriander", "Sweet potato", "Gram", "Tobacco",
]

SEASONS = ["Kharif", "Rabi", "Summer", "Autumn", "Winter", "Whole Year"]

_DISTRICT_SYNONYMS = {
    "KANCHEEPURAM": "KANCHIPURAM",
    "KANYAKUMARI": "KANNIYAKUMARI",
    "TUTICORIN": "THOOTHUKUDI",
    "VILLUPURAM": "VILUPPURAM",
    "THE NILGIRIS": "NILGIRIS",
}

# Districts carved out after the 2019 agriculture census used to train the
# model have no history under their own name yet — fall back to the parent
# district they were split from.
_NEW_DISTRICT_PARENT = {
    "KALLAKURICHI": "VILUPPURAM",
    "MAYILADUTHURAI": "NAGAPATTINAM",
    "RANIPET": "VELLORE",
    "TENKASI": "TIRUNELVELI",
    "TIRUPATHUR": "VELLORE",
    "CHENGALPATTU": "KANCHIPURAM",
}

_KNOWN_AG_DISTRICTS = set(_features_df["District"].str.upper().unique())


def _normalize_district(district):
    """Map a display district name to the District label the model/encoders were trained on."""
    key = district.strip().upper()
    key = _DISTRICT_SYNONYMS.get(key, key)
    if key not in _KNOWN_AG_DISTRICTS:
        key = _NEW_DISTRICT_PARENT.get(key, key)
    return key


# --------------------------------------------------------------------------
# District crop priority: real historical Area per (District, Crop), used to
# rank the "Select Crop" dropdown and the dashboard's "Crops Grown Near You"
# widget so crops actually cultivated in the farmer's district surface
# first, with the rest shown as options worth exploring for that area.
# --------------------------------------------------------------------------
_DISTRICT_CROP_AREA = _features_df.groupby(["District", "Crop"])["Area"].sum().reset_index()


def get_district_crop_priority(district):
    """Returns (grown, other): CROPS actually cultivated in `district` (real
    historical Area data), ranked by total area descending, followed by the
    remaining CROPS not currently grown there."""
    ag_district = _normalize_district(district)
    sub = _DISTRICT_CROP_AREA[_DISTRICT_CROP_AREA["District"] == ag_district]
    grown = [c for c in sub.sort_values("Area", ascending=False)["Crop"].tolist() if c in CROPS]
    other = [c for c in CROPS if c not in grown]
    return grown, other


_MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_sowing_window(crop, season):
    """Month/day sowing window text for a (crop, season) pair, independent
    of any particular year - for informational display (e.g. the dashboard
    crop-info popup) rather than a dated recommendation."""
    entry = SOWING_CALENDAR.get((crop, season))
    if not entry:
        return None
    sm, sd = entry["start"]
    em, ed = entry["end"]
    return f"{sd} {_MONTH_ABBR[sm]} – {ed} {_MONTH_ABBR[em]}"


def get_crop_profile(district, crop):
    """Real historical profile for one (district, crop) pair: which seasons
    it's grown in there, total cultivated area, average climate conditions
    during those cultivation years, and average yield. Returns None if
    there's no recorded history for this crop in the district.

    Yield is safe to show here (see scripts/06_agriculture_data/
    02_clean_agriculture_data.py): the raw government production data had a
    ~100x unit inconsistency for every crop, corrected there before this
    file is ever built. yield_category compares this district's average
    against that CROP's own quantiles (_YIELD_QUANTILES), not a global
    split, so it means "how did {crop} do here" rather than "which crop is
    this" - see the comment by _YIELD_QUANTILES above.
    """
    ag_district = _normalize_district(district)
    sub = _features_df[(_features_df["District"] == ag_district) & (_features_df["Crop"] == crop)]
    if sub.empty:
        return None

    season_area = sub.groupby("Season")["Area"].sum().sort_values(ascending=False)
    avg_yield = float(sub["Yield"].mean())
    yield_q1, yield_q2 = _YIELD_QUANTILES.get(crop, (0, 0))
    yield_category = "Low" if avg_yield <= yield_q1 else "Medium" if avg_yield <= yield_q2 else "High"

    return {
        "seasons": season_area.index.tolist(),
        "total_area": round(float(sub["Area"].sum()), 0),
        "avg_rainfall": round(float(sub["TotalRainfall"].mean()), 0),
        # 2 decimals here (not the usual 1) because district-wide temperature
        # barely varies crop to crop (it's weather, not agronomy) - e.g.
        # Thanjavur ranges ~27.9-28.3 across every crop grown there, so 1
        # decimal collapses distinct crops to the same displayed value and
        # reads as a bug rather than as genuinely near-identical climate.
        "avg_temperature": round(float(sub["AvgTemperature"].mean()), 2),
        "avg_humidity": round(float(sub["AvgHumidity"].mean()), 0),
        "avg_yield": round(avg_yield, 2),
        "yield_category": yield_category,
        "years_recorded": int(sub["Year"].nunique()),
    }


# --------------------------------------------------------------------------
# TNAU-style reference sowing calendar
# --------------------------------------------------------------------------
# Built from well-established Tamil Nadu agronomic-extension practice
# (general agronomic knowledge, not transcribed from a specific TNAU PDF
# in this repo — cross-check against the department's official TNAU crop
# calendar if citation-level precision is needed for the review).
# Sugarcane and Banana each have 2-3 valid planting windows in real TN
# practice; the dataset only tracks a single "Whole Year" bucket for both,
# so this picks the single most common planting window for each.
SOWING_CALENDAR = {
    ("Rice", "Kharif"):          {"start": (6, 5),   "end": (6, 25)},
    ("Rice", "Winter"):          {"start": (8, 15),  "end": (9, 15)},
    ("Rice", "Autumn"):          {"start": (9, 20),  "end": (10, 15)},
    ("Rice", "Summer"):          {"start": (1, 1),   "end": (1, 20)},
    ("Groundnut", "Kharif"):     {"start": (6, 15),  "end": (7, 15)},
    ("Groundnut", "Rabi"):       {"start": (1, 1),   "end": (1, 31)},
    ("Cotton(lint)", "Kharif"):  {"start": (8, 1),   "end": (8, 30)},
    ("Cotton(lint)", "Rabi"):    {"start": (10, 1),  "end": (10, 20)},
    ("Maize", "Kharif"):         {"start": (6, 15),  "end": (7, 10)},
    ("Maize", "Rabi"):           {"start": (10, 1),  "end": (10, 25)},
    ("Bajra", "Kharif"):         {"start": (6, 15),  "end": (7, 15)},
    ("Bajra", "Rabi"):           {"start": (9, 15),  "end": (10, 10)},
    ("Ragi", "Kharif"):          {"start": (6, 15),  "end": (7, 15)},
    ("Ragi", "Rabi"):            {"start": (9, 15),  "end": (10, 10)},
    ("Sugarcane", "Whole Year"): {"start": (12, 15), "end": (1, 15)},
    ("Banana", "Whole Year"):    {"start": (8, 15),  "end": (9, 15)},

    # 17 crops added alongside the crop-coverage expansion (see CROPS above).
    # Same caveat as the original 8: general agronomic-extension knowledge
    # for TN, not transcribed from an official TNAU PDF - cross-check against
    # the department's published crop calendar for citation-level precision.
    ("Urad", "Kharif"):           {"start": (7, 1),   "end": (7, 31)},
    ("Urad", "Rabi"):             {"start": (9, 15),  "end": (10, 15)},
    ("Moong(Green Gram)", "Kharif"): {"start": (6, 15), "end": (7, 15)},
    ("Moong(Green Gram)", "Rabi"):   {"start": (9, 15), "end": (10, 15)},
    ("Sesamum", "Kharif"):        {"start": (7, 1),   "end": (7, 31)},
    ("Sesamum", "Rabi"):          {"start": (9, 1),   "end": (9, 30)},
    ("Jowar", "Kharif"):          {"start": (6, 15),  "end": (7, 15)},
    ("Jowar", "Rabi"):            {"start": (9, 15),  "end": (10, 15)},
    ("Sunflower", "Kharif"):      {"start": (6, 15),  "end": (7, 15)},
    ("Sunflower", "Rabi"):        {"start": (10, 1),  "end": (10, 31)},
    ("Horse-gram", "Kharif"):     {"start": (7, 1),   "end": (7, 31)},
    ("Horse-gram", "Rabi"):       {"start": (9, 15),  "end": (10, 15)},
    ("Onion", "Kharif"):          {"start": (6, 15),  "end": (7, 15)},
    ("Onion", "Rabi"):            {"start": (10, 1),  "end": (10, 31)},
    ("Arhar/Tur", "Kharif"):      {"start": (6, 15),  "end": (7, 15)},
    ("Dry chillies", "Whole Year"): {"start": (8, 15), "end": (9, 15)},
    ("Tapioca", "Whole Year"):    {"start": (4, 15),  "end": (5, 15)},
    ("Turmeric", "Whole Year"):   {"start": (4, 15),  "end": (5, 15)},
    ("Cashewnut", "Whole Year"):  {"start": (6, 1),   "end": (7, 15)},
    ("Small millets", "Kharif"):  {"start": (6, 15),  "end": (7, 15)},
    ("Coriander", "Whole Year"):  {"start": (9, 15),  "end": (10, 15)},
    ("Sweet potato", "Whole Year"): {"start": (8, 1),  "end": (8, 31)},
    ("Gram", "Rabi"):             {"start": (10, 1),  "end": (10, 31)},
    ("Tobacco", "Whole Year"):    {"start": (8, 15),  "end": (9, 15)},
}

# Familiar Tamil Nadu paddy-season names — agronomically meaningful only
# for Rice; used purely for display (see translations.translate_season).
RICE_SEASON_TN_NAME = {
    "Kharif": "Kuruvai",
    "Winter": "Samba",
    "Summer": "Navarai",
}

_DEFAULT_SOWING = {"start": (6, 15), "end": (7, 15)}


# --------------------------------------------------------------------------
# Category thresholds — must match scripts/07_data_integration/03_feature_engineering.py
# exactly, since that's what the encoders/model were trained on.
# --------------------------------------------------------------------------
def _temperature_category(temp):
    if temp < 25:
        return "Cool"
    elif temp < 30:
        return "Normal"
    return "Hot"


def _rainfall_category(rain):
    if rain < 800:
        return "Low"
    elif rain < 1200:
        return "Medium"
    return "High"


def _humidity_category(humidity):
    if humidity < 60:
        return "Low"
    elif humidity < 75:
        return "Medium"
    return "High"


def _wind_category(wind):
    if wind < 2:
        return "Low"
    elif wind < 3.5:
        return "Medium"
    return "High"


# --------------------------------------------------------------------------
# Step 1: Climate Data Retrieval (real historical averages)
# --------------------------------------------------------------------------
def retrieve_climate_data(district, crop, season, year):
    """Average historical climate/agriculture features for (district, crop,
    season), falling back to (district, season) then (district) when the
    exact combination has no recorded history."""
    ag_district = _normalize_district(district)
    df = _features_df

    subset = df[(df["District"] == ag_district) & (df["Crop"] == crop) & (df["Season"] == season)]
    if subset.empty:
        subset = df[(df["District"] == ag_district) & (df["Season"] == season)]
    if subset.empty:
        subset = df[df["District"] == ag_district]
    if subset.empty:
        subset = df[(df["Crop"] == crop) & (df["Season"] == season)]
    if subset.empty:
        subset = df

    means = subset[_NUMERIC_HISTORY_COLUMNS].mean()

    return {
        "ag_district": ag_district,
        "Area": round(float(means["Area"]), 2),
        "AvgTemperature": round(float(means["AvgTemperature"]), 2),
        "MaxTemperature": round(float(means["MaxTemperature"]), 2),
        "MinTemperature": round(float(means["MinTemperature"]), 2),
        "TotalRainfall": round(float(means["TotalRainfall"]), 2),
        "AvgRainfall": round(float(means["AvgRainfall"]), 2),
        "MaxRainfall": round(float(means["MaxRainfall"]), 2),
        "AvgHumidity": round(float(means["AvgHumidity"]), 2),
        "AvgWindSpeed": round(float(means["AvgWindSpeed"]), 2),
        "RainyDays": round(float(means["RainyDays"]), 2),
        "TemperatureStd": round(float(means["TemperatureStd"]), 2),
        "RainfallStd": round(float(means["RainfallStd"]), 2),
    }


# --------------------------------------------------------------------------
# Step 2: Machine Learning Prediction (real XGBoost inference)
# --------------------------------------------------------------------------
def predict_yield(district, crop, season, year, climate):
    ag_district = climate["ag_district"]
    temp_cat = _temperature_category(climate["AvgTemperature"])
    rain_cat = _rainfall_category(climate["TotalRainfall"])
    humidity_cat = _humidity_category(climate["AvgHumidity"])
    wind_cat = _wind_category(climate["AvgWindSpeed"])

    row = {
        "District": _encoders["District"].transform([ag_district])[0],
        "Year": year,
        "Season": _encoders["Season"].transform([season])[0],
        "Crop": _encoders["Crop"].transform([crop])[0],
        "Area": climate["Area"],
        "AvgTemperature": climate["AvgTemperature"],
        "MaxTemperature": climate["MaxTemperature"],
        "MinTemperature": climate["MinTemperature"],
        "TotalRainfall": climate["TotalRainfall"],
        "AvgRainfall": climate["AvgRainfall"],
        "MaxRainfall": climate["MaxRainfall"],
        "AvgHumidity": climate["AvgHumidity"],
        "AvgWindSpeed": climate["AvgWindSpeed"],
        "RainyDays": climate["RainyDays"],
        "TemperatureStd": climate["TemperatureStd"],
        "RainfallStd": climate["RainfallStd"],
        "Temperature_Category": _encoders["Temperature_Category"].transform([temp_cat])[0],
        "Rainfall_Category": _encoders["Rainfall_Category"].transform([rain_cat])[0],
        "Humidity_Category": _encoders["Humidity_Category"].transform([humidity_cat])[0],
        "Wind_Category": _encoders["Wind_Category"].transform([wind_cat])[0],
    }
    feature_row = pd.DataFrame([[row[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)

    predicted_yield = float(_model.predict(feature_row)[0])
    yield_q1, yield_q2 = _YIELD_QUANTILES.get(crop, (0, 0))
    if predicted_yield <= yield_q1:
        yield_category = "Low"
    elif predicted_yield <= yield_q2:
        yield_category = "Medium"
    else:
        yield_category = "High"

    return predicted_yield, yield_category, rain_cat


# --------------------------------------------------------------------------
# Step 3: Climate Risk Assessment (real rainfall category + real 21-year trend)
# --------------------------------------------------------------------------
def assess_climate_risk(district, rainfall_category):
    trend_row = _rainfall_trends.loc[district] if district in _rainfall_trends.index else None
    pct_change = float(trend_row["Percentage Change (%)"]) if trend_row is not None else 0.0
    trend_label = str(trend_row["Trend"]) if trend_row is not None else "Stable"

    if rainfall_category == "Low":
        drought_risk = "High" if pct_change <= -20 else "Moderate"
    elif rainfall_category == "Medium":
        drought_risk = "Moderate" if pct_change <= -20 else "Low"
    else:
        drought_risk = "Low"

    if rainfall_category == "High":
        flood_risk = "High" if pct_change >= 20 else "Moderate"
    elif rainfall_category == "Medium":
        flood_risk = "Moderate" if pct_change >= 20 else "Low"
    else:
        flood_risk = "Low"

    risk_rank = {"Low": 0, "Moderate": 1, "High": 2}
    overall_risk = {0: "Low", 1: "Moderate", 2: "High"}[max(risk_rank[drought_risk], risk_rank[flood_risk])]

    return drought_risk, flood_risk, overall_risk, pct_change, trend_label


# --------------------------------------------------------------------------
# Step 4: Sowing window (TNAU-style reference calendar)
# --------------------------------------------------------------------------
def get_sowing_window(crop, season):
    entry = SOWING_CALENDAR.get((crop, season), _DEFAULT_SOWING)
    start_month, start_day = entry["start"]
    end_month, end_day = entry["end"]

    today = datetime.now()
    year = today.year if today.month <= start_month else today.year + 1
    start_date = datetime(year, start_month, start_day)
    end_year = year + 1 if end_month < start_month else year
    end_date = datetime(end_year, end_month, end_day)

    best_sowing_date = start_date + (end_date - start_date) / 2

    return start_date, end_date, best_sowing_date, year


# --------------------------------------------------------------------------
# Step 5: Confidence score (data-driven, from yield tertile + risk)
# --------------------------------------------------------------------------
def build_confidence(yield_category, overall_risk):
    base = {"High": 88, "Medium": 74, "Low": 58}[yield_category]
    risk_penalty = {"Low": 0, "Moderate": 8, "High": 18}[overall_risk]
    return max(40, min(97, base - risk_penalty))


def generate_suggestions(crop, overall_risk, drought_risk, flood_risk, best_sowing_date, pct_change, trend_label):
    """Returns structured suggestion codes (key + params), not rendered text,
    so the UI can render them in whichever language the viewer currently has
    selected — see translations.render_suggestions(). Stored as JSON in the
    recommendations table rather than pre-rendered English."""
    suggestions = [{"key": "prepare_land", "date": best_sowing_date}]

    if flood_risk in ("Moderate", "High"):
        suggestions.append({"key": "drainage_ready"})
    if drought_risk in ("Moderate", "High"):
        suggestions.append({"key": "irrigation_plan"})
    if overall_risk == "High":
        suggestions.append({"key": "short_duration_variety"})

    suggestions.append({"key": "rainfall_trend_note", "trend": trend_label, "pct": pct_change})

    return suggestions[:4]


def predict_crop_recommendation(district, crop, season):
    """Orchestrates the full pipeline and returns a complete recommendation payload."""
    start_date, end_date, best_sowing_date, year = get_sowing_window(crop, season)

    climate = retrieve_climate_data(district, crop, season, year)
    predicted_yield, yield_category, rainfall_category = predict_yield(district, crop, season, year, climate)
    drought_risk, flood_risk, overall_risk, pct_change, trend_label = assess_climate_risk(district, rainfall_category)
    confidence_score = build_confidence(yield_category, overall_risk)

    suggestions = generate_suggestions(
        crop, overall_risk, drought_risk, flood_risk,
        best_sowing_date.strftime("%d %b %Y"), pct_change, trend_label,
    )

    return {
        "district": district,
        "crop": crop,
        "season": season,
        "sowing_window": f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}",
        "best_sowing_date": best_sowing_date.strftime("%d %b %Y"),
        "expected_rainfall": climate["TotalRainfall"],
        "avg_temperature": climate["AvgTemperature"],
        "humidity": climate["AvgHumidity"],
        "wind_speed": climate["AvgWindSpeed"],
        "drought_risk": drought_risk,
        "flood_risk": flood_risk,
        "overall_risk": overall_risk,
        "climate_stability_score": round(100 - {"Low": 0, "Moderate": 20, "High": 40}[overall_risk] - min(climate["RainfallStd"] / 20, 15), 1),
        "confidence_score": confidence_score,
        "predicted_yield": round(predicted_yield, 1),
        "yield_category": yield_category,
        "suggestions": suggestions,
    }


# --------------------------------------------------------------------------
# Monsoon Insights — the real 21-year rainfall/temperature trend for a
# district, for the dedicated Monsoon Insights page. Independent of
# predict_crop_recommendation() (no crop/season needed) so a farmer can
# see their district's long-term climate trend on its own.
# --------------------------------------------------------------------------
def _trend_payload(row):
    if row is None:
        return None
    return {
        "start_year": int(row["Start Year"]),
        "end_year": int(row["End Year"]),
        "years_analysed": int(row["Years Analysed"]),
        "r2": round(float(row["R2 Score"]), 3),
        "pct_change": round(float(row["Percentage Change (%)"]), 1),
        "trend": row["Trend"],
        "strength": row["Strength"],
    }


def get_climate_trend(district):
    """Real year-by-year rainfall/temperature series (2005-2025) plus the
    linear-regression trend summary for a district, used by the Monsoon
    Insights page. Returns None if the district isn't in the climate data
    (shouldn't happen for any of TN_DISTRICTS)."""
    key = district.strip()
    history = _yearly_summary[_yearly_summary["District"] == key].sort_values("Year")
    if history.empty:
        return None

    years = history["Year"].tolist()
    rainfall = history["TotalRainfall"].round(1).tolist()
    temperature = history["AvgTemperature"].round(1).tolist()

    rain_slope, rain_intercept = (float(v) for v in np.polyfit(years, rainfall, 1))
    temp_slope, temp_intercept = (float(v) for v in np.polyfit(years, temperature, 1))
    rainfall_trendline = [round(rain_slope * y + rain_intercept, 1) for y in years]
    temperature_trendline = [round(temp_slope * y + temp_intercept, 1) for y in years]

    driest = history.loc[history["TotalRainfall"].idxmin()]
    wettest = history.loc[history["TotalRainfall"].idxmax()]

    recent_rainfall_avg = float(history.tail(5)["TotalRainfall"].mean())
    rainfall_category = _rainfall_category(recent_rainfall_avg)
    drought_risk, flood_risk, overall_risk, _, _ = assess_climate_risk(key, rainfall_category)

    return {
        "district": key,
        "years": years,
        "rainfall": rainfall,
        "temperature": temperature,
        "rainfall_trendline": rainfall_trendline,
        "temperature_trendline": temperature_trendline,
        "rainfall_trend": _trend_payload(_rainfall_trends.loc[key] if key in _rainfall_trends.index else None),
        "temperature_trend": _trend_payload(_temperature_trends.loc[key] if key in _temperature_trends.index else None),
        "driest_year": {"year": int(driest["Year"]), "rainfall": round(float(driest["TotalRainfall"]), 1)},
        "wettest_year": {"year": int(wettest["Year"]), "rainfall": round(float(wettest["TotalRainfall"]), 1)},
        "recent_rainfall_avg": round(recent_rainfall_avg, 1),
        "rainfall_category": rainfall_category,
        "drought_risk": drought_risk,
        "flood_risk": flood_risk,
        "overall_risk": overall_risk,
    }
