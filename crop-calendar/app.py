"""
Climate-Smart Crop Calendar Recommender for Tamil Nadu
=========================================================
Main Flask application.

Run with:
    python app.py

The app connects to PostgreSQL (see db.py / PGADMIN_SETUP.md for how to
create the database and configure .env) and auto-creates its tables on
first run, seeding a demo farmer account:
    Mobile: 9876543210
    Password: demo1234
"""

import os
import json
import random
from datetime import datetime, timedelta
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

from db import get_db
from models.ml_model import (
    predict_crop_recommendation, get_climate_trend, get_district_crop_priority,
    get_crop_profile, format_sowing_window, TN_DISTRICTS, CROPS, SEASONS
)
from models.weather_utils import get_weather_forecast, get_climate_alerts
from translations import (
    translate, translate_district, translate_crop, translate_season,
    render_suggestions, render_notification,
)

# --------------------------------------------------------------------------
# App configuration
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "climate-smart-crop-calendar-secret-key-change-in-production"
)
app.config["SESSION_PERMANENT"] = False

# TN_DISTRICTS, CROPS, SEASONS now come from models.ml_model — the same
# real district/crop/season lists the trained model actually knows.


def init_db():
    conn = get_db()

    # Postgres uses SERIAL (not AUTOINCREMENT) for auto-incrementing ids,
    # and TO_CHAR(...) instead of SQLite's datetime('now') for a text-typed
    # timestamp default - kept as TEXT (not a native TIMESTAMP column) so
    # the existing templates' farmer['created_at'].split(' ')[0] etc. keep
    # working unchanged against the same 'YYYY-MM-DD HH:MM:SS' string shape.
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS farmers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT,
            district TEXT NOT NULL,
            farm_size REAL NOT NULL,
            preferred_crop TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS')
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id SERIAL PRIMARY KEY,
            farmer_id INTEGER NOT NULL,
            district TEXT NOT NULL,
            crop TEXT NOT NULL,
            season TEXT NOT NULL,
            sowing_window TEXT NOT NULL,
            best_sowing_date TEXT NOT NULL,
            expected_rainfall REAL,
            avg_temperature REAL,
            humidity REAL,
            wind_speed REAL,
            drought_risk TEXT,
            flood_risk TEXT,
            overall_risk TEXT,
            confidence_score INTEGER,
            suggestions TEXT,
            recommendation_date TEXT DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
            FOREIGN KEY (farmer_id) REFERENCES farmers (id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            farmer_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            notification_text TEXT NOT NULL,
            created_at TEXT DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
            FOREIGN KEY (farmer_id) REFERENCES farmers (id)
        );
        """
    )
    conn.commit()

    # Seed a demo farmer so the app is explorable immediately
    existing = conn.execute("SELECT id FROM farmers WHERE mobile = ?", ("9876543210",)).fetchone()
    if existing is None:
        # Postgres has no sqlite-style cursor.lastrowid - RETURNING id is
        # the standard way to get the new row's id back from an INSERT.
        new_row = conn.execute(
            """INSERT INTO farmers
               (name, mobile, email, district, farm_size, preferred_crop, password)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               RETURNING id""",
            (
                "Ramesh Kumar", "9876543210", "ramesh@example.com",
                "Thanjavur", 5.0, "Rice",
                generate_password_hash("demo1234"),
            ),
        ).fetchone()
        farmer_id = new_row["id"]

        # title/notification_text store an i18n key (+ JSON params for the
        # text) rather than pre-rendered English, so notifications also
        # follow whichever language the viewer currently has selected —
        # see translations.render_notification().
        demo_notifications = [
            ("weather", "notif_heavy_rain_title", "notif_heavy_rain_text",
             {"rainfall": "80-100mm", "district": "Thanjavur"}),
            ("monsoon", "notif_monsoon_update_title", "notif_monsoon_update_text",
             {"days": "5"}),
            ("sowing", "notif_sowing_reminder_title", "notif_sowing_reminder_text",
             {"crop": "Rice", "season": "Kharif"}),
            ("system", "notif_rec_updated_title", "notif_rec_updated_text", {}),
        ]
        for category, title_key, text_key, params in demo_notifications:
            conn.execute(
                """INSERT INTO notifications (farmer_id, category, title, notification_text)
                   VALUES (?, ?, ?, ?)""",
                (farmer_id, category, title_key, json.dumps({"key": text_key, "params": params})),
            )
        conn.commit()

    conn.close()


# --------------------------------------------------------------------------
# Auth helpers
# --------------------------------------------------------------------------
def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "farmer_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


def current_farmer():
    conn = get_db()
    farmer = conn.execute(
        "SELECT * FROM farmers WHERE id = ?", (session.get("farmer_id"),)
    ).fetchone()
    conn.close()
    return farmer


# --------------------------------------------------------------------------
# Language / i18n helpers
# --------------------------------------------------------------------------
def get_lang():
    return session.get("lang", "en")


@app.context_processor
def inject_i18n():
    """Makes t(), tr_district(), tr_crop(), tr_season() and current_lang
    available inside every Jinja template without passing them explicitly
    from each view function."""
    lang = get_lang()
    return {
        "t": lambda key: translate(key, lang),
        "tr_district": lambda name: translate_district(name, lang),
        "tr_crop": lambda name: translate_crop(name, lang),
        "tr_season": lambda name, crop=None: translate_season(name, lang, crop),
        "current_lang": lang,
    }


@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    if lang_code in ("en", "ta"):
        session["lang"] = lang_code
    target = request.referrer or url_for("splash")
    return redirect(target)


# --------------------------------------------------------------------------
# Routes: Splash / Auth
# --------------------------------------------------------------------------
@app.route("/")
def splash():
    if "farmer_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("splash.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        district = request.form.get("district", "")
        farm_size = request.form.get("farm_size", "")
        preferred_crop = request.form.get("preferred_crop", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # ---- Server-side validation ----
        errors = []
        if not name or len(name) < 3:
            errors.append("Please enter your full name (min 3 characters).")
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            errors.append("Please enter a valid 10-digit mobile number.")
        if district not in TN_DISTRICTS:
            errors.append("Please select a valid district.")
        if preferred_crop not in CROPS:
            errors.append("Please select a preferred crop.")
        try:
            farm_size_val = float(farm_size)
            if farm_size_val <= 0:
                raise ValueError
        except ValueError:
            errors.append("Farm size must be a positive number.")
            farm_size_val = None
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM farmers WHERE mobile = ?", (mobile,)
        ).fetchone()
        if existing:
            errors.append("This mobile number is already registered.")

        if errors:
            conn.close()
            for e in errors:
                flash(e, "error")
            return render_template(
                "register.html", districts=TN_DISTRICTS, crops=CROPS, form=request.form
            )

        conn.execute(
            """INSERT INTO farmers
               (name, mobile, email, district, farm_size, preferred_crop, password)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, mobile, email, district, farm_size_val, preferred_crop,
             generate_password_hash(password)),
        )
        conn.commit()
        conn.close()

        flash("Registration successful! Please login to continue.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", districts=TN_DISTRICTS, crops=CROPS, form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form.get("mobile", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        farmer = conn.execute(
            "SELECT * FROM farmers WHERE mobile = ?", (mobile,)
        ).fetchone()
        conn.close()

        if farmer and check_password_hash(farmer["password"], password):
            session["farmer_id"] = farmer["id"]
            session["farmer_name"] = farmer["name"]
            flash(f"Welcome back, {farmer['name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid mobile number or password.", "error")

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        # Placeholder flow: in production this would send an OTP/reset link.
        flash("If this mobile number is registered, a reset link has been sent.", "success")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


# --------------------------------------------------------------------------
# Routes: Dashboard
# --------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    farmer = current_farmer()
    weather_today, rainfall_trend, temperature_trend = get_weather_forecast(farmer["district"])
    alerts = get_climate_alerts(farmer["district"])
    grown_crops, other_crops = get_district_crop_priority(farmer["district"])
    crop_labels = {c: translate_crop(c, get_lang()) for c in CROPS}

    conn = get_db()
    unread_count = conn.execute(
        "SELECT COUNT(*) as c FROM notifications WHERE farmer_id = ?", (farmer["id"],)
    ).fetchone()["c"]
    conn.close()

    return render_template(
        "dashboard.html",
        farmer=farmer,
        weather_today=weather_today,
        rainfall_trend=rainfall_trend,
        temperature_trend=temperature_trend,
        alerts=alerts,
        unread_count=unread_count,
        top_crops=grown_crops[:4],
        new_crop_ideas=other_crops[:2],
        crop_labels=crop_labels,
    )


# --------------------------------------------------------------------------
# Routes: Weather Forecast
# --------------------------------------------------------------------------
@app.route("/weather")
@login_required
def weather():
    farmer = current_farmer()
    _, _, _ = None, None, None
    forecast_days = get_weather_forecast(farmer["district"], days=7, detailed=True)
    return render_template("weather.html", farmer=farmer, forecast_days=forecast_days)


# --------------------------------------------------------------------------
# Routes: Monsoon Insights (real 21-year rainfall/temperature trend)
# --------------------------------------------------------------------------
@app.route("/monsoon")
@login_required
def monsoon():
    farmer = current_farmer()
    trend = get_climate_trend(farmer["district"])
    return render_template(
        "monsoon.html",
        farmer=farmer,
        districts=TN_DISTRICTS,
        crops=CROPS,
        seasons=SEASONS,
        trend=trend,
    )


@app.route("/api/monsoon-trend/<district>")
@login_required
def api_monsoon_trend(district):
    if district not in TN_DISTRICTS:
        return jsonify({"error": "Invalid district."}), 400
    trend = get_climate_trend(district)
    if trend is None:
        return jsonify({"error": "No climate data for this district."}), 404
    return jsonify(trend)


# --------------------------------------------------------------------------
# Routes: Crop Recommendation
# --------------------------------------------------------------------------
@app.route("/recommendation")
@login_required
def recommendation():
    farmer = current_farmer()
    grown_crops, other_crops = get_district_crop_priority(farmer["district"])
    crop_labels = {c: translate_crop(c, get_lang()) for c in CROPS}
    return render_template(
        "recommendation.html",
        farmer=farmer,
        districts=TN_DISTRICTS,
        crops=CROPS,
        seasons=SEASONS,
        grown_crops=grown_crops,
        other_crops=other_crops,
        crop_labels=crop_labels,
    )


@app.route("/api/district-crops/<district>")
@login_required
def api_district_crops(district):
    """Crop priority for `district`, used by the recommendation form to
    re-rank the Select Crop dropdown when the farmer picks a different
    district than the one they registered with."""
    if district not in TN_DISTRICTS:
        return jsonify({"error": "Invalid district."}), 400
    grown, other = get_district_crop_priority(district)
    return jsonify({"grown": grown, "other": other})


@app.route("/api/crop-info/<district>/<crop>")
@login_required
def api_crop_info(district, crop):
    """Powers the dashboard's crop-detail popup: seasons, sowing windows,
    cultivated area and average climate conditions for one (district, crop)
    pair, from real historical data."""
    if district not in TN_DISTRICTS or crop not in CROPS:
        return jsonify({"error": "Invalid selection."}), 400

    profile = get_crop_profile(district, crop)
    if profile is None:
        return jsonify({"error": "No historical cultivation data for this crop in this district."}), 404

    lang = get_lang()
    seasons = profile.pop("seasons")
    profile["crop"] = crop
    profile["crop_label"] = translate_crop(crop, lang)
    profile["district_label"] = translate_district(district, lang)
    profile["seasons_display"] = [
        {
            "label": translate_season(s, lang, crop),
            "sowing_window": format_sowing_window(crop, s),
        }
        for s in seasons
    ]
    return jsonify(profile)


@app.route("/api/analyze", methods=["POST"])
@login_required
def analyze():
    """
    AI process flow:
      1. Climate Data Retrieval
      2. Monsoon Shift Detection
      3. Rainfall Analysis
      4. Climate Risk Assessment
      5. Machine Learning Prediction
    """
    data = request.get_json(force=True)
    district = data.get("district")
    crop = data.get("crop")
    season = data.get("season")

    if district not in TN_DISTRICTS or crop not in CROPS or season not in SEASONS:
        return jsonify({"error": "Invalid input selection."}), 400

    result = predict_crop_recommendation(district, crop, season)

    conn = get_db()
    new_row = conn.execute(
        """INSERT INTO recommendations
           (farmer_id, district, crop, season, sowing_window, best_sowing_date,
            expected_rainfall, avg_temperature, humidity, wind_speed,
            drought_risk, flood_risk, overall_risk, confidence_score, suggestions)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           RETURNING id""",
        (
            session["farmer_id"], district, crop, season,
            result["sowing_window"], result["best_sowing_date"],
            result["expected_rainfall"], result["avg_temperature"],
            result["humidity"], result["wind_speed"],
            result["drought_risk"], result["flood_risk"], result["overall_risk"],
            result["confidence_score"], json.dumps(result["suggestions"]),
        ),
    ).fetchone()
    rec_id = new_row["id"]
    conn.commit()
    conn.close()

    result["recommendation_id"] = rec_id
    session["last_recommendation_id"] = rec_id
    return jsonify(result)


@app.route("/result")
@app.route("/result/<int:rec_id>")
@login_required
def result(rec_id=None):
    farmer = current_farmer()
    rec_id = rec_id or session.get("last_recommendation_id")

    conn = get_db()
    if rec_id:
        rec = conn.execute(
            "SELECT * FROM recommendations WHERE id = ? AND farmer_id = ?",
            (rec_id, farmer["id"]),
        ).fetchone()
    else:
        rec = conn.execute(
            "SELECT * FROM recommendations WHERE farmer_id = ? ORDER BY id DESC LIMIT 1",
            (farmer["id"],),
        ).fetchone()
    conn.close()

    if rec is None:
        flash("No recommendation found. Please analyze a new one.", "warning")
        return redirect(url_for("recommendation"))

    suggestions = []
    if rec["suggestions"]:
        try:
            codes = json.loads(rec["suggestions"])
            suggestions = render_suggestions(codes, get_lang())
        except (ValueError, TypeError):
            # Legacy rows stored pipe-joined, pre-rendered English text.
            suggestions = rec["suggestions"].split("|")
    return render_template(
        "result.html", farmer=farmer, rec=rec, suggestions=suggestions,
        window_year=_sowing_window_year(rec),
    )


# --------------------------------------------------------------------------
# Routes: Calendar
# --------------------------------------------------------------------------
def _sowing_window_year(rec):
    """The best_sowing_date's year if it's later than the current year
    (i.e. this year's window already passed and the recommendation rolled
    forward to the next occurrence) - lets the templates surface that
    context to the farmer instead of silently jumping a year ahead."""
    if not rec:
        return None
    try:
        rec_year = datetime.strptime(rec["best_sowing_date"], "%d %b %Y").year
    except (ValueError, TypeError):
        return None
    return rec_year if rec_year > datetime.now().year else None


@app.route("/calendar")
@login_required
def calendar_view():
    farmer = current_farmer()
    conn = get_db()
    rec = conn.execute(
        "SELECT * FROM recommendations WHERE farmer_id = ? ORDER BY id DESC LIMIT 1",
        (farmer["id"],),
    ).fetchone()
    conn.close()
    return render_template(
        "calendar.html", farmer=farmer, rec=rec, window_year=_sowing_window_year(rec)
    )


@app.route("/api/save-recommendation/<int:rec_id>", methods=["POST"])
@login_required
def save_recommendation(rec_id):
    conn = get_db()
    rec = conn.execute(
        "SELECT * FROM recommendations WHERE id = ? AND farmer_id = ?",
        (rec_id, session["farmer_id"]),
    ).fetchone()
    if rec:
        text_payload = json.dumps({"key": "notif_rec_saved_text", "params": {"crop": rec["crop"]}})
        conn.execute(
            """INSERT INTO notifications (farmer_id, category, title, notification_text)
               VALUES (?, 'system', 'notif_rec_saved_title', ?)""",
            (session["farmer_id"], text_payload),
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True})


# --------------------------------------------------------------------------
# Routes: Notifications
# --------------------------------------------------------------------------
def _localize_notification(row, lang):
    """title/notification_text hold an i18n key (+ JSON params for the
    text) for app-generated notifications — see translations.render_notification().
    Falls back to the raw stored text unchanged for legacy plain-English rows."""
    title = translate(row["title"], lang)

    text = row["notification_text"]
    try:
        payload = json.loads(text)
        params = dict(payload.get("params", {}))
        if "season" in params:
            params["season"] = translate_season(params["season"], lang, params.get("crop"))
        if "crop" in params:
            params["crop"] = translate_crop(params["crop"], lang)
        if "district" in params:
            params["district"] = translate_district(params["district"], lang)
        text = render_notification(payload["key"], params, lang)
    except (ValueError, TypeError, KeyError):
        pass  # legacy row: notification_text is already plain rendered text

    return {**dict(row), "title": title, "notification_text": text}


@app.route("/notifications")
@login_required
def notifications():
    farmer = current_farmer()
    lang = get_lang()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM notifications WHERE farmer_id = ? ORDER BY id DESC",
        (farmer["id"],),
    ).fetchall()
    conn.close()
    all_notifications = [_localize_notification(row, lang) for row in rows]
    return render_template("notifications.html", farmer=farmer, notifications=all_notifications)


# --------------------------------------------------------------------------
# Routes: Profile
# --------------------------------------------------------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    farmer = current_farmer()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        district = request.form.get("district", "")
        farm_size = request.form.get("farm_size", "")
        preferred_crop = request.form.get("preferred_crop", "")

        conn = get_db()
        conn.execute(
            """UPDATE farmers SET name=?, email=?, district=?, farm_size=?, preferred_crop=?
               WHERE id=?""",
            (name, email, district, farm_size, preferred_crop, farmer["id"]),
        )
        conn.commit()
        conn.close()
        session["farmer_name"] = name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    conn = get_db()
    recent_recs = conn.execute(
        "SELECT * FROM recommendations WHERE farmer_id = ? ORDER BY id DESC LIMIT 5",
        (farmer["id"],),
    ).fetchall()
    conn.close()

    return render_template(
        "profile.html", farmer=farmer, districts=TN_DISTRICTS, crops=CROPS, recent_recs=recent_recs
    )


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
# Runs at import time (not just under __main__) so tables get created both
# for local `python app.py` AND when a production server like gunicorn
# imports this module directly (gunicorn never executes the __main__ block
# below, so init_db() has to live out here to run in both cases).
init_db()

if __name__ == "__main__":
    # FLASK_DEBUG defaults to on for local dev (matches the previous
    # hardcoded debug=True) but must be off wherever this app is reachable
    # from the public internet - Werkzeug's debugger allows arbitrary code
    # execution to anyone who can trigger an unhandled exception, so
    # render.yaml explicitly sets FLASK_DEBUG=0 for the deployed service.
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
