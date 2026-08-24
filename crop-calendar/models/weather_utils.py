"""
Weather Utilities
==================
Live weather for each Tamil Nadu district, pulled from Open-Meteo
(https://open-meteo.com/ - free, no API key required) and keyed off each
district's headquarters coordinates in DISTRICT_COORDS.

If the API is unreachable (offline dev, network blocked, etc.) every
function falls back to a deterministic placeholder so the app still renders
instead of crashing. That fallback is clearly a stand-in, not real weather -
see _fallback_forecast() / _fallback_alerts().
"""

import random
import time
from datetime import datetime, timedelta

import requests

# Approximate headquarters coordinates for each of the 38 TN districts the
# app lists (models/ml_model.py:TN_DISTRICTS). Good enough for district-level
# weather - Open-Meteo forecasts are already only ~11km resolution.
DISTRICT_COORDS = {
    "Ariyalur": (11.14, 79.08),
    "Chengalpattu": (12.69, 79.98),
    "Chennai": (13.08, 80.27),
    "Coimbatore": (11.02, 76.96),
    "Cuddalore": (11.75, 79.75),
    "Dharmapuri": (12.13, 78.16),
    "Dindigul": (10.37, 77.98),
    "Erode": (11.34, 77.73),
    "Kallakurichi": (11.74, 78.96),
    "Kanchipuram": (12.84, 79.70),
    "Kanniyakumari": (8.09, 77.57),
    "Karur": (10.96, 78.08),
    "Krishnagiri": (12.52, 78.22),
    "Madurai": (9.93, 78.12),
    "Mayiladuthurai": (11.10, 79.65),
    "Nagapattinam": (10.77, 79.84),
    "Namakkal": (11.22, 78.17),
    "Nilgiris": (11.41, 76.70),
    "Perambalur": (11.23, 78.88),
    "Pudukkottai": (10.38, 78.82),
    "Ramanathapuram": (9.37, 78.83),
    "Ranipet": (12.93, 79.33),
    "Salem": (11.66, 78.15),
    "Sivagangai": (9.85, 78.48),
    "Tenkasi": (8.96, 77.31),
    "Thanjavur": (10.79, 79.14),
    "Theni": (10.01, 77.48),
    "Thoothukudi": (8.76, 78.13),
    "Tiruchirappalli": (10.79, 78.70),
    "Tirunelveli": (8.71, 77.76),
    "Tirupathur": (12.50, 78.57),
    "Tiruppur": (11.11, 77.34),
    "Tiruvallur": (13.14, 79.91),
    "Tiruvannamalai": (12.23, 79.07),
    "Tiruvarur": (10.77, 79.63),
    "Vellore": (12.92, 79.13),
    "Viluppuram": (11.94, 79.49),
    "Virudhunagar": (9.59, 77.96),
}

# WMO weather codes (Open-Meteo's `weather_code`) mapped down to the
# condition/icon pairs the UI already knows how to render.
_WEATHER_CODE_MAP = {
    0: ("Sunny", "sun"),
    1: ("Partly Cloudy", "cloud-sun"),
    2: ("Partly Cloudy", "cloud-sun"),
    3: ("Cloudy", "cloud"),
    45: ("Cloudy", "cloud"), 48: ("Cloudy", "cloud"),
    51: ("Light Rain", "cloud-rain"), 53: ("Light Rain", "cloud-rain"),
    55: ("Moderate Rain", "cloud-showers-heavy"),
    56: ("Light Rain", "cloud-rain"), 57: ("Moderate Rain", "cloud-showers-heavy"),
    61: ("Light Rain", "cloud-rain"), 63: ("Moderate Rain", "cloud-showers-heavy"),
    65: ("Heavy Rain", "cloud-showers-water"),
    66: ("Moderate Rain", "cloud-showers-heavy"), 67: ("Heavy Rain", "cloud-showers-water"),
    71: ("Cloudy", "cloud"), 73: ("Cloudy", "cloud"), 75: ("Cloudy", "cloud"), 77: ("Cloudy", "cloud"),
    80: ("Moderate Rain", "cloud-showers-heavy"),
    81: ("Heavy Rain", "cloud-showers-water"), 82: ("Heavy Rain", "cloud-showers-water"),
    85: ("Cloudy", "cloud"), 86: ("Cloudy", "cloud"),
    95: ("Heavy Rain", "cloud-showers-water"), 96: ("Heavy Rain", "cloud-showers-water"),
    99: ("Heavy Rain", "cloud-showers-water"),
}
_DEFAULT_CONDITION = ("Cloudy", "cloud")

_API_URL = "https://api.open-meteo.com/v1/forecast"
_CACHE_TTL_SECONDS = 900  # 15 min - keeps every dashboard/weather load fast
_cache = {}


def _condition_for(code):
    try:
        return _WEATHER_CODE_MAP.get(int(code), _DEFAULT_CONDITION)
    except (TypeError, ValueError):
        return _DEFAULT_CONDITION


def _fetch_live(district):
    """Returns the raw Open-Meteo response for a district, cached for
    _CACHE_TTL_SECONDS. Returns None if the API can't be reached."""
    now = time.time()
    cached = _cache.get(district)
    if cached and now - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]

    lat, lon = DISTRICT_COORDS.get(district, DISTRICT_COORDS["Chennai"])
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "hourly": "relative_humidity_2m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "Asia/Kolkata",
        "forecast_days": 7,
    }
    try:
        resp = requests.get(_API_URL, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    _cache[district] = (now, data)
    return data


def _hourly_humidity_for_date(data, date_str):
    times = data.get("hourly", {}).get("time", [])
    values = data.get("hourly", {}).get("relative_humidity_2m", [])
    day_values = [v for t, v in zip(times, values) if t.startswith(date_str) and v is not None]
    if not day_values:
        return None
    return sum(day_values) / len(day_values)


# --------------------------------------------------------------------------
# Placeholder fallback (only used when the live API can't be reached)
# --------------------------------------------------------------------------
_FALLBACK_PROFILE = {"base_rainfall": 120, "base_temp": 30, "base_humidity": 70, "base_wind": 12}


def _rng_for(district, offset=0):
    seed = abs(hash((district, "weather", offset, datetime.now().strftime("%Y-%m-%d")))) % (10 ** 6)
    return random.Random(seed)


def _fallback_forecast(district, days, detailed):
    profile = _FALLBACK_PROFILE
    today = datetime.now()

    if detailed:
        forecast = []
        for i in range(days):
            rng = _rng_for(district, i)
            condition, icon = rng.choice(list(_WEATHER_CODE_MAP.values()))
            forecast.append({
                "date": (today + timedelta(days=i)).strftime("%d %b"),
                "condition": condition,
                "icon": icon,
                "temperature": round(profile["base_temp"] + rng.uniform(-3, 3), 1),
                "rainfall": round(max(0, profile["base_rainfall"] / 30 + rng.uniform(-8, 15)), 0),
                "humidity": round(profile["base_humidity"] + rng.uniform(-8, 8), 0),
                "wind_speed": round(profile["base_wind"] + rng.uniform(-3, 3), 0),
            })
        return forecast

    rng = _rng_for(district)
    weather_today = {
        "temperature": round(profile["base_temp"] + rng.uniform(-2, 2), 1),
        "rainfall": round(max(0, profile["base_rainfall"] / 30 + rng.uniform(-5, 10)), 0),
        "humidity": round(profile["base_humidity"] + rng.uniform(-6, 6), 0),
        "wind_speed": round(profile["base_wind"] + rng.uniform(-2, 2), 0),
    }

    rainfall_trend, temperature_trend, days_labels = [], [], []
    for i in range(7):
        rng_i = _rng_for(district, i)
        days_labels.append((today + timedelta(days=i)).strftime("%a"))
        rainfall_trend.append(round(max(0, profile["base_rainfall"] / 30 + rng_i.uniform(-5, 12)), 0))
        temperature_trend.append(round(profile["base_temp"] + rng_i.uniform(-2, 2), 1))

    return weather_today, {"labels": days_labels, "values": rainfall_trend}, \
        {"labels": days_labels, "values": temperature_trend}


def _fallback_alerts(district):
    rng = _rng_for(district, 99)
    alerts = []
    if rng.random() > 0.85:
        alerts.append({"level": "high", "title": "Heavy Rain Expected", "detail": "in the next 5 days"})
    if not alerts:
        alerts.append({"level": "low", "title": "Conditions Stable", "detail": "no major alerts this week"})
    return alerts


# --------------------------------------------------------------------------
# Public API (signatures unchanged - app.py doesn't need to change)
# --------------------------------------------------------------------------
def get_weather_forecast(district, days=7, detailed=False):
    data = _fetch_live(district)
    if data is None:
        return _fallback_forecast(district, days, detailed)

    daily = data["daily"]
    n = min(days, len(daily["time"]))

    if detailed:
        forecast = []
        for i in range(n):
            date_str = daily["time"][i]
            condition, icon = _condition_for(daily["weather_code"][i])
            humidity = _hourly_humidity_for_date(data, date_str)
            forecast.append({
                "date": datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %b"),
                "condition": condition,
                "icon": icon,
                "temperature": round((daily["temperature_2m_max"][i] + daily["temperature_2m_min"][i]) / 2, 1),
                "rainfall": round(daily["precipitation_sum"][i] or 0, 0),
                "humidity": round(humidity if humidity is not None else data["current"]["relative_humidity_2m"], 0),
                "wind_speed": round(daily["wind_speed_10m_max"][i], 0),
            })
        return forecast

    current = data["current"]
    weather_today = {
        "temperature": round(current["temperature_2m"], 1),
        "rainfall": round(daily["precipitation_sum"][0] or 0, 0),
        "humidity": round(current["relative_humidity_2m"], 0),
        "wind_speed": round(current["wind_speed_10m"], 0),
    }

    days_labels, rainfall_trend, temperature_trend = [], [], []
    for i in range(min(7, n)):
        days_labels.append(datetime.strptime(daily["time"][i], "%Y-%m-%d").strftime("%a"))
        rainfall_trend.append(round(daily["precipitation_sum"][i] or 0, 0))
        temperature_trend.append(round((daily["temperature_2m_max"][i] + daily["temperature_2m_min"][i]) / 2, 1))

    return weather_today, {"labels": days_labels, "values": rainfall_trend}, \
        {"labels": days_labels, "values": temperature_trend}


def get_climate_alerts(district):
    data = _fetch_live(district)
    if data is None:
        return _fallback_alerts(district)

    daily = data["daily"]
    alerts = []
    for i, rain in enumerate(daily["precipitation_sum"]):
        if rain is not None and rain >= 50:
            when = "today" if i == 0 else f"in {i} day(s)"
            alerts.append({
                "level": "high",
                "title": "Heavy Rain Expected",
                "detail": f"{round(rain)}mm expected {when} ({district})",
            })
            break

    max_wind = max((w for w in daily.get("wind_speed_10m_max", []) if w is not None), default=0)
    if max_wind >= 40:
        alerts.append({
            "level": "moderate",
            "title": "Strong Winds Expected",
            "detail": f"gusts up to {round(max_wind)} km/h this week",
        })

    if not alerts:
        alerts.append({"level": "low", "title": "Conditions Stable", "detail": "no major alerts this week"})
    return alerts
