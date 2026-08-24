# Climate-Smart Crop Calendar Recommender — Tamil Nadu

AI-powered Flask web app that helps farmers identify the best crop sowing
window using climate data, monsoon-shift detection, rainfall analysis, and
a machine-learning-style risk/confidence score.

Installable as a mobile app (PWA) — see [PGADMIN_SETUP.md](PGADMIN_SETUP.md) for opening it
on Android and adding it to the home screen.

## Tech Stack
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js (charts), Font Awesome (icons) — also
  installable as a Progressive Web App (`static/manifest.json`, `static/js/sw.js`)
- **Backend:** Python Flask
- **Database:** PostgreSQL (`db.py`; see [PGADMIN_SETUP.md](PGADMIN_SETUP.md) for creating
  the database in pgAdmin and configuring `.env`)
- **ML pipeline:** `models/ml_model.py` loads the real trained XGBoost yield
  model (`models/xgboost_model.pkl`, 97.0% test R², best of the three models
  compared - see `output/machine_learning/model_comparison.csv`) plus the real historical
  climate/agriculture dataset (`dataset/final/climate_agriculture_features.csv`)
  and the real 21-year rainfall trend analysis
  (`output/climate_intelligence/reports/rainfall_trends.csv`) to produce
  data-backed recommendations — no random placeholders.
- **Live weather:** `models/weather_utils.py` calls the free Open-Meteo API
  (no key required) for real per-district temperature/rainfall/humidity/wind,
  cached 15 minutes; falls back to a clearly-labeled placeholder only if the
  API is unreachable.

## Project Structure
```
crop-calendar/
├── app.py                     # Flask routes, auth, DB access
├── db.py                      # PostgreSQL connection helper (psycopg2)
├── .env.example                # copy to .env and fill in your DB password
├── requirements.txt
├── models/
│   ├── ml_model.py            # 5-step AI recommendation pipeline
│   └── weather_utils.py       # live weather (Open-Meteo) + climate alerts
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   ├── js/sw.js                # service worker (PWA offline caching)
│   ├── manifest.json            # PWA install metadata
│   ├── icons/                    # PWA app icons
│   └── images/
└── templates/
    ├── base.html               # sidebar + topbar shell
    ├── splash.html              # Page 1 – Splash screen
    ├── register.html            # Page 2 – Farmer registration
    ├── login.html                # Page 3 – Login
    ├── forgot_password.html
    ├── dashboard.html            # Page 4 – Farmer dashboard
    ├── weather.html               # Page 5 – Weather forecast
    ├── recommendation.html        # Page 6 – Crop recommendation input
    ├── result.html                 # Page 7 – Recommendation result
    ├── calendar.html                # Page 8 – Calendar view
    ├── notifications.html            # Page 9 – Notification center
    └── profile.html                   # Page 10 – Farmer profile
```

## Setup & Run

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database in pgAdmin and configure .env
#    (full walkthrough in PGADMIN_SETUP.md)
cp .env.example .env            # then fill in your postgres password

# 4. Run the app
python app.py
```

The app starts at **http://localhost:5000**. Its tables and the demo account
are created automatically on first launch, the same way SQLite used to —
see [PGADMIN_SETUP.md](PGADMIN_SETUP.md) for the pgAdmin steps and how to
open the app on an Android phone as an installable PWA.

### Demo login
```
Mobile:    9876543210
Password:  demo1234
```

## Database Schema

**farmers** — id, name, mobile, email, district, farm_size, preferred_crop, password, created_at
**recommendations** — id, farmer_id, district, crop, season, sowing_window, best_sowing_date, expected_rainfall, avg_temperature, humidity, wind_speed, drought_risk, flood_risk, overall_risk, confidence_score, suggestions, recommendation_date
**notifications** — id, farmer_id, category, title, notification_text, created_at

## AI Process Flow (`models/ml_model.py`)
1. **Climate Data Retrieval** — `retrieve_climate_data()`: averages real
   historical climate/agriculture features for the chosen district+crop+season,
   with graceful fallback (district+season, then district-only) when the exact
   combination has no recorded history.
2. **Machine Learning Prediction** — `predict_yield()`: real XGBoost inference
   (the trained model predicts Yield in kg/ha; there's no sowing-date ground
   truth in the data, so the sowing window comes from a TNAU-style reference
   calendar instead, see step 4).
3. **Climate Risk Assessment** — `assess_climate_risk()`: drought/flood risk
   from the real rainfall category plus the district's real 21-year rainfall
   trend.
4. **Sowing Window** — `get_sowing_window()`: TNAU-style reference calendar
   per crop+season (see `SOWING_CALENDAR` in the module — built from general
   Tamil Nadu agronomic-extension practice, not transcribed from a specific
   cited TNAU PDF; cross-check against the department's official crop
   calendar if citation-level precision is needed).
5. **Confidence Score** — `build_confidence()`: derived from how the
   predicted yield compares to the district's yield tertile and the overall
   risk level.

The app supports the real 38 Tamil Nadu districts, 25 crops, and 6
government-census seasons (Kharif, Rabi, Summer, Autumn, Winter, Whole Year)
— matching what the trained model actually knows. The 25 crops are the
original 8 food/cash crops (Rice, Groundnut, Cotton(lint), Sugarcane, Maize,
Bajra, Ragi, Banana) plus 17 more added later covering pulses, oilseeds,
millets, spices and plantation crops (Urad, Moong, Sesamum, Jowar, Sunflower,
Horse-gram, Onion, Arhar/Tur, Dry chillies, Tapioca, Turmeric, Cashewnut,
Small millets, Coriander, Sweet potato, Gram, Tobacco) — see
`scripts/06_agriculture_data/02_clean_agriculture_data.py` for exactly which
other TN crops were considered and why they weren't included (Coconut,
Mango/Grapes/Papaya, Tea/Coffee/Rubber). For Rice specifically, the UI also
shows the familiar Tamil Nadu paddy-season name in brackets (Kharif →
Kuruvai, Winter → Samba, Summer → Navarai), since that mapping is
agronomically meaningful only for paddy.

## Language Toggle (English ⇄ Tamil)
The app ships with a working English/Tamil switch — look for the **EN | தமிழ்**
pill in the top-right corner (auth pages show it top-right of the screen).

- Selecting a language stores it in the Flask session (`translations.py` +
  `get_lang()` / `set_language()` in `app.py`), so it persists across every
  page for that login session.
- All navigation, buttons, form labels, and page headings are translated via
  the `t('key')` helper, injected into every template through a
  `context_processor`.
- District, crop, and season **names** are also localized (e.g. "Rice" ↔
  "நெல்") via `tr_district()`, `tr_crop()`, `tr_season()` — but the
  underlying `value` sent to the backend stays in English, so no route or
  database logic had to change.
- **Known limitation:** AI suggestion text and notification messages are
  currently generated in English only (`models/ml_model.py`,
  `models/weather_utils.py`) since they're dynamically composed, not static
  UI strings. Translating those would mean having `predict_crop_recommendation()`
  accept a `lang` parameter and return localized suggestion text — a
  reasonable next step if full end-to-end Tamil is needed.

To add more languages later: add a new top-level key (e.g. `"hi"`) to
`TRANSLATIONS` in `translations.py`, add a matching toggle link in
`base.html` and the auth page templates, and it works the same way.

## Future Features (placeholders wired in the UI)
- GPS-based district auto-detection
- Full Tamil localization of AI-generated suggestions/notifications (see above)
- Mobile app version
- Push notifications
- AI chat assistant for farmers
- Coconut back in the crop list, once its production-data unit issue
  (~100,000x duplicate-row gap, not the ~100x gap fixed for every other
  crop) is properly investigated

## Notes
- Passwords are hashed with Werkzeug's `generate_password_hash`.
- Session-based authentication via Flask's built-in `session`.
- "Download PDF Report" / "Download Calendar PDF" currently trigger the
  browser print dialog (`window.print()`) as a lightweight placeholder —
  swap for a proper PDF export (e.g. `weasyprint` or `reportlab`) when
  ready for production.
