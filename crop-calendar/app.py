"""
Climate-Smart Crop Calendar Recommender for Tamil Nadu
=========================================================
Main Flask application.

Run with:
    python app.py

The app will auto-create the SQLite database (database/crop_calendar.db)
on first run and seed it with a demo farmer account:
    Mobile: 9876543210
    Password: demo1234
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash

from models.ml_model import predict_crop_recommendation
from models.weather_utils import get_weather_forecast, get_climate_alerts
from translations import (
    translate, translate_district, translate_crop, translate_season
)

# --------------------------------------------------------------------------
# App configuration
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "crop_calendar.db")

app = Flask(__name__)
app.secret_key = "climate-smart-crop-calendar-secret-key-change-in-production"
app.config["SESSION_PERMANENT"] = False

TN_DISTRICTS = [
    "Chennai", "Thanjavur", "Madurai", "Coimbatore",
    "Trichy", "Salem", "Tirunelveli", "Erode"
]
CROPS = ["Rice", "Groundnut", "Cotton", "Sugarcane", "Maize", "Millets", "Banana"]
SEASONS = ["Kuruvai", "Samba", "Navarai"]


# --------------------------------------------------------------------------
# Database helpers
# --------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT,
            district TEXT NOT NULL,
            farm_size REAL NOT NULL,
            preferred_crop TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            recommendation_date TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (farmer_id) REFERENCES farmers (id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            notification_text TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (farmer_id) REFERENCES farmers (id)
        );
        """
    )
    conn.commit()

    # Seed a demo farmer so the app is explorable immediately
    cur.execute("SELECT id FROM farmers WHERE mobile = ?", ("9876543210",))
    if cur.fetchone() is None:
        cur.execute(
            """INSERT INTO farmers
               (name, mobile, email, district, farm_size, preferred_crop, password)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                "Ramesh Kumar", "9876543210", "ramesh@example.com",
                "Thanjavur", 5.0, "Rice",
                generate_password_hash("demo1234"),
            ),
        )
        farmer_id = cur.lastrowid

        demo_notifications = [
            ("weather", "Heavy Rain Expected Tomorrow",
             "Heavy rainfall of 80-100mm expected in Thanjavur district."),
            ("monsoon", "Monsoon Update",
             "Southwest monsoon has arrived 5 days early in Tamil Nadu."),
            ("sowing", "Sowing Reminder",
             "Tomorrow is an ideal day for sowing Rice (Kuruvai)."),
            ("system", "Recommendation Updated",
             "Your crop recommendation has been updated. Check now."),
        ]
        for category, title, text in demo_notifications:
            cur.execute(
                """INSERT INTO notifications (farmer_id, category, title, notification_text)
                   VALUES (?, ?, ?, ?)""",
                (farmer_id, category, title, text),
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
        "tr_season": lambda name: translate_season(name, lang),
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
# Routes: Crop Recommendation
# --------------------------------------------------------------------------
@app.route("/recommendation")
@login_required
def recommendation():
    farmer = current_farmer()
    return render_template(
        "recommendation.html",
        farmer=farmer,
        districts=TN_DISTRICTS,
        crops=CROPS,
        seasons=SEASONS,
    )


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
    conn.execute(
        """INSERT INTO recommendations
           (farmer_id, district, crop, season, sowing_window, best_sowing_date,
            expected_rainfall, avg_temperature, humidity, wind_speed,
            drought_risk, flood_risk, overall_risk, confidence_score, suggestions)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            session["farmer_id"], district, crop, season,
            result["sowing_window"], result["best_sowing_date"],
            result["expected_rainfall"], result["avg_temperature"],
            result["humidity"], result["wind_speed"],
            result["drought_risk"], result["flood_risk"], result["overall_risk"],
            result["confidence_score"], "|".join(result["suggestions"]),
        ),
    )
    rec_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
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

    suggestions = rec["suggestions"].split("|") if rec["suggestions"] else []
    return render_template("result.html", farmer=farmer, rec=rec, suggestions=suggestions)


# --------------------------------------------------------------------------
# Routes: Calendar
# --------------------------------------------------------------------------
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
    return render_template("calendar.html", farmer=farmer, rec=rec)


@app.route("/api/save-recommendation/<int:rec_id>", methods=["POST"])
@login_required
def save_recommendation(rec_id):
    conn = get_db()
    rec = conn.execute(
        "SELECT * FROM recommendations WHERE id = ? AND farmer_id = ?",
        (rec_id, session["farmer_id"]),
    ).fetchone()
    if rec:
        conn.execute(
            """INSERT INTO notifications (farmer_id, category, title, notification_text)
               VALUES (?, 'system', 'Recommendation Saved',
               ? || ' calendar saved to your profile.')""",
            (session["farmer_id"], rec["crop"]),
        )
        conn.commit()
    conn.close()
    return jsonify({"success": True})


# --------------------------------------------------------------------------
# Routes: Notifications
# --------------------------------------------------------------------------
@app.route("/notifications")
@login_required
def notifications():
    farmer = current_farmer()
    conn = get_db()
    all_notifications = conn.execute(
        "SELECT * FROM notifications WHERE farmer_id = ? ORDER BY id DESC",
        (farmer["id"],),
    ).fetchall()
    conn.close()
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
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
