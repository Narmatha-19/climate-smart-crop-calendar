"""
Weather Utilities
==================
Placeholder weather data generator. Swap `get_weather_forecast()` and
`get_climate_alerts()` internals for a real provider (e.g. OpenWeatherMap,
IMD API, Open-Meteo) when wiring up the "Real-Time Weather API" future
feature. The function signatures are designed to stay stable so templates
and app.py do not need to change.
"""

import random
from datetime import datetime, timedelta

from models.ml_model import DISTRICT_CLIMATE_PROFILE

CONDITIONS = [
    ("Sunny", "sun"),
    ("Cloudy", "cloud"),
    ("Light Rain", "cloud-rain"),
    ("Moderate Rain", "cloud-showers-heavy"),
    ("Heavy Rain", "cloud-showers-water"),
    ("Partly Cloudy", "cloud-sun"),
]


def _rng_for(district, offset=0):
    seed = abs(hash((district, "weather", offset, datetime.now().strftime("%Y-%m-%d")))) % (10 ** 6)
    return random.Random(seed)


def get_weather_forecast(district, days=7, detailed=False):
    profile = DISTRICT_CLIMATE_PROFILE.get(district, DISTRICT_CLIMATE_PROFILE["Thanjavur"])
    today = datetime.now()

    if detailed:
        forecast = []
        for i in range(days):
            rng = _rng_for(district, i)
            condition, icon = rng.choice(CONDITIONS)
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

    rainfall_trend = []
    temperature_trend = []
    days_labels = []
    for i in range(7):
        rng_i = _rng_for(district, i)
        days_labels.append((today + timedelta(days=i)).strftime("%a"))
        rainfall_trend.append(round(max(0, profile["base_rainfall"] / 30 + rng_i.uniform(-5, 12)), 0))
        temperature_trend.append(round(profile["base_temp"] + rng_i.uniform(-2, 2), 1))

    return weather_today, {"labels": days_labels, "values": rainfall_trend}, \
        {"labels": days_labels, "values": temperature_trend}


def get_climate_alerts(district):
    profile = DISTRICT_CLIMATE_PROFILE.get(district, DISTRICT_CLIMATE_PROFILE["Thanjavur"])
    rng = _rng_for(district, 99)

    alerts = []
    if profile["base_rainfall"] > 150 or rng.random() > 0.5:
        alerts.append({
            "level": "high",
            "title": "Heavy Rain Expected",
            "detail": "in the next 5 days",
        })
    if rng.random() > 0.6:
        alerts.append({
            "level": "moderate",
            "title": "Moderate Flood Risk",
            "detail": f"in your district ({district})",
        })
    if not alerts:
        alerts.append({
            "level": "low",
            "title": "Conditions Stable",
            "detail": "no major alerts this week",
        })
    return alerts
