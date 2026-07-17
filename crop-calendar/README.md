# Climate-Smart Crop Calendar Recommender — Tamil Nadu

AI-powered Flask web app that helps farmers identify the best crop sowing
window using climate data, monsoon-shift detection, rainfall analysis, and
a machine-learning-style risk/confidence score.

## Tech Stack
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js (charts), Font Awesome (icons)
- **Backend:** Python Flask
- **Database:** SQLite (auto-created on first run)
- **ML pipeline:** placeholder rule-based engine in `models/ml_model.py`,
  structured so it can be swapped for a trained XGBoost/Scikit-Learn model
  without touching `app.py` or the templates.

## Project Structure
```
crop-calendar/
├── app.py                     # Flask routes, auth, DB access
├── requirements.txt
├── database/
│   └── crop_calendar.db       # created automatically on first run
├── models/
│   ├── ml_model.py            # 5-step AI recommendation pipeline
│   └── weather_utils.py       # weather + climate alert placeholders
├── static/
│   ├── css/style.css
│   ├── js/script.js
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

# 3. Run the app
python app.py
```

The app starts at **http://localhost:5000**. The SQLite database and demo
account are created automatically on first launch.

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
1. **Climate Data Retrieval** — `retrieve_climate_data()`
2. **Monsoon Shift Detection** — `detect_monsoon_shift()`
3. **Rainfall Analysis** — `analyze_rainfall()`
4. **Climate Risk Assessment** — `assess_climate_risk()`
5. **Machine Learning Prediction** — `ml_predict_sowing_window()`

Each stage is an isolated function so it can be replaced with a real model
(e.g. an XGBoost regressor trained on IMD rainfall data, monsoon onset
records, and historical yield) without changing any route or template.

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
- Real-Time Weather API integration (currently `models/weather_utils.py`)
- GPS-based district auto-detection
- Full Tamil localization of AI-generated suggestions/notifications (see above)
- Mobile app version
- Push notifications
- AI chat assistant for farmers

## Notes
- Passwords are hashed with Werkzeug's `generate_password_hash`.
- Session-based authentication via Flask's built-in `session`.
- "Download PDF Report" / "Download Calendar PDF" currently trigger the
  browser print dialog (`window.print()`) as a lightweight placeholder —
  swap for a proper PDF export (e.g. `weasyprint` or `reportlab`) when
  ready for production.
