# -*- coding: utf-8 -*-
"""
Translations for the Climate-Smart Crop Calendar UI.

Usage in app.py:
    from translations import TRANSLATIONS, CROP_TA, DISTRICT_TA, SEASON_TA

`t(key)` (injected as a Jinja global via context_processor) looks up the
current session language and falls back to English, then to the raw key,
so a missing translation never breaks a page — it just shows English.
"""

TRANSLATIONS = {
    "en": {
        # ---- Brand / Sidebar / Topbar ----
        "brand_name": "Climate-Smart",
        "brand_sub": "CROP CALENDAR",
        "nav_dashboard": "Dashboard",
        "nav_recommendation": "Crop Recommendation",
        "nav_weather": "Weather Forecast",
        "nav_calendar": "My Calendar",
        "nav_notifications": "Notifications",
        "nav_profile": "Profile",
        "nav_logout": "Logout",

        # ---- Splash ----
        "splash_eyebrow": "Built for Tamil Nadu Farmers",
        "splash_title_pre": "AI-Powered",
        "splash_title_highlight": "Climate Smart",
        "splash_title_post": "Farming",
        "splash_tagline": "Get the best sowing window for your crop, powered by monsoon shift detection, rainfall analysis, and machine-learning risk scoring — tuned for your district.",
        "btn_login": "Login",
        "btn_register": "Register",

        # ---- Login ----
        "login_heading": "Welcome back to<br>smarter farming decisions.",
        "login_hero_text": "Log in to view your personalized climate alerts, crop recommendations, and sowing calendar.",
        "login_title": "Login to Your Account",
        "login_subtitle": "Enter your credentials to access your dashboard",
        "label_mobile": "Mobile Number",
        "label_password": "Password",
        "placeholder_mobile": "Enter your 10-digit mobile number",
        "placeholder_password": "Enter your password",
        "forgot_password": "Forgot Password?",
        "no_account": "Don't have an account?",
        "register_here": "Register here",
        "demo_login_note": "Demo login — Mobile: <strong>9876543210</strong> · Password: <strong>demo1234</strong>",

        # ---- Register ----
        "register_heading": "Join thousands of farmers<br>making climate-smart choices.",
        "register_hero_text": "Register in under a minute and get AI-backed sowing recommendations tailored to your district.",
        "register_title": "Create New Account",
        "register_subtitle": "Register as a Farmer",
        "label_name": "Full Name",
        "label_preferred_crop": "Preferred Crop",
        "label_email": "Email (Optional)",
        "label_district": "District",
        "label_farm_size": "Farm Size (in acres)",
        "label_confirm_password": "Confirm Password",
        "placeholder_name": "Enter your full name",
        "placeholder_email": "Enter your email",
        "placeholder_mobile_reg": "Enter mobile number",
        "placeholder_farm_size": "Enter farm size",
        "placeholder_password_create": "Create a password",
        "placeholder_password_confirm": "Confirm your password",
        "select_crop_placeholder": "Select preferred crop",
        "select_district_placeholder": "Select your district",
        "already_account": "Already have an account?",
        "login_here": "Login here",

        # ---- Forgot Password ----
        "forgot_heading": "Forgot your password?<br>No worries.",
        "forgot_hero_text": "Enter your registered mobile number and we'll help you regain access to your account.",
        "forgot_title": "Reset Password",
        "forgot_subtitle": "We'll send a reset link to your registered mobile number",
        "placeholder_mobile_registered": "Enter your registered mobile number",
        "btn_send_reset": "Send Reset Link",
        "remembered_password": "Remembered your password?",
        "back_to_login": "Back to Login",

        # ---- Dashboard ----
        "welcome": "Welcome",
        "district_label": "District",
        "todays_weather": "Today's Weather",
        "temperature": "Temperature",
        "rainfall": "Rainfall",
        "humidity": "Humidity",
        "wind_speed": "Wind Speed",
        "this_week": "This Week",
        "rainfall_forecast": "Rainfall Forecast",
        "next_7_days": "Next 7 Days (mm)",
        "climate_alerts": "Climate Alerts",
        "view_all_alerts": "View All Alerts",
        "temperature_trend": "Temperature Trend",
        "quick_actions": "Quick Actions",

        # ---- Weather ----
        "weather_forecast": "Weather Forecast",
        "day_forecast_for": "7-Day Forecast for",
        "average": "Average",
        "col_date": "Date",
        "col_weather": "Weather",
        "col_temp": "Temp (°C)",
        "col_rainfall": "Rainfall (mm)",
        "col_humidity": "Humidity (%)",
        "col_wind": "Wind (km/h)",
        "forecast_table_title": "7 Day Weather Forecast",

        # ---- Recommendation ----
        "crop_recommendation": "Crop Recommendation",
        "rec_subtitle": "Select details to get AI-based crop calendar recommendation",
        "select_district": "Select District",
        "select_crop": "Select Crop",
        "select_season": "Select Season",
        "analyze_btn": "Analyze & Get Recommendation",
        "analyzing": "Analyzing climate data...",
        "historical_data": "Historical Data Analysis",
        "ai_prediction_model": "AI Prediction Model",
        "smart_calendar": "Smart Crop Calendar",
        "about_rec_title": "About this recommendation:",
        "about_rec_text": "Our AI model analyzes historical weather data, monsoon patterns, and soil conditions to recommend the best sowing window for your selected crop and season.",

        # ---- Result ----
        "ai_result_title": "AI Recommendation Result",
        "ai_result_subtitle": "Based on climate analysis and ML prediction",
        "recommended_crop": "Recommended Crop",
        "season": "Season",
        "recommended_window": "Recommended Window",
        "best_sowing_date": "Best Sowing Date",
        "weather_prediction": "Weather Prediction",
        "expected_rainfall": "Expected Rainfall",
        "avg_temperature": "Avg Temperature",
        "risk_assessment": "Risk Assessment",
        "drought_risk": "Drought Risk",
        "flood_risk": "Flood Risk",
        "overall_risk": "Overall Risk",
        "model_confidence": "Model Confidence",
        "high_confidence": "High Confidence",
        "ai_suggestions": "AI Suggestions",
        "download_pdf": "Download PDF Report",
        "add_to_calendar": "Add to My Calendar",
        "risk_low": "Low",
        "risk_moderate": "Moderate",
        "risk_high": "High",

        # ---- Calendar ----
        "crop_calendar_title": "Crop Calendar",
        "based_on_latest": "Based on your latest recommendation",
        "no_rec_yet": "No recommendation yet",
        "next": "Next",
        "recommended_days": "Recommended Days",
        "acceptable_days": "Acceptable Days",
        "high_risk_days": "High Risk Days",
        "download_calendar_pdf": "Download Calendar PDF",
        "save_recommendation": "Save Recommendation",
        "saved": "Saved",
        "no_rec_generated": "You haven't generated a crop recommendation yet.",
        "get_one_now": "Get one now",

        # ---- Notifications ----
        "notifications_title": "Notifications",
        "notifications_subtitle": "Stay updated with important alerts and recommendations",
        "tab_all": "All",
        "tab_weather": "Weather Alerts",
        "tab_monsoon": "Monsoon Alerts",
        "tab_sowing": "Sowing Reminders",
        "tab_system": "System Alerts",
        "no_notifications": "No notifications yet.",

        # ---- Profile ----
        "farmer_profile": "Farmer Profile",
        "profile_subtitle": "Manage your personal information and preferences",
        "edit_profile": "Edit Profile",
        "cancel": "Cancel",
        "farm_size": "Farm Size",
        "preferred_crop": "Preferred Crop",
        "member_since": "Member Since",
        "save_changes": "Save Changes",
        "recent_recommendations": "Recent Recommendations",
        "no_recs_generated": "No recommendations generated yet.",
        "view": "View",
        "acres": "Acres",
        "no_email_added": "No email added",
    },

    "ta": {
        "brand_name": "காலநிலை-ஸ்மார்ட்",
        "brand_sub": "பயிர் நாட்காட்டி",
        "nav_dashboard": "டாஷ்போர்டு",
        "nav_recommendation": "பயிர் பரிந்துரை",
        "nav_weather": "வானிலை முன்னறிவிப்பு",
        "nav_calendar": "எனது நாட்காட்டி",
        "nav_notifications": "அறிவிப்புகள்",
        "nav_profile": "சுயவிவரம்",
        "nav_logout": "வெளியேறு",

        "splash_eyebrow": "தமிழ்நாடு விவசாயிகளுக்காக உருவாக்கப்பட்டது",
        "splash_title_pre": "AI-இயங்கும்",
        "splash_title_highlight": "காலநிலை ஸ்மார்ட்",
        "splash_title_post": "விவசாயம்",
        "splash_tagline": "பருவமழை மாற்றம் கண்டறிதல், மழைப்பொழிவு பகுப்பாய்வு மற்றும் இயந்திர கற்றல் அபாய மதிப்பீட்டின் மூலம், உங்கள் மாவட்டத்திற்கு ஏற்ற சிறந்த விதைப்பு காலத்தைப் பெறுங்கள்.",
        "btn_login": "உள்நுழைய",
        "btn_register": "பதிவு செய்ய",

        "login_heading": "மீண்டும் வரவேற்கிறோம்<br>சிறந்த விவசாய முடிவுகளுக்கு.",
        "login_hero_text": "உங்கள் தனிப்பயன் காலநிலை எச்சரிக்கைகள், பயிர் பரிந்துரைகள் மற்றும் விதைப்பு நாட்காட்டியைப் பார்க்க உள்நுழையவும்.",
        "login_title": "உங்கள் கணக்கில் உள்நுழையவும்",
        "login_subtitle": "உங்கள் டாஷ்போர்டை அணுக விவரங்களை உள்ளிடவும்",
        "label_mobile": "மொபைல் எண்",
        "label_password": "கடவுச்சொல்",
        "placeholder_mobile": "10-இலக்க மொபைல் எண்ணை உள்ளிடவும்",
        "placeholder_password": "கடவுச்சொல்லை உள்ளிடவும்",
        "forgot_password": "கடவுச்சொல் மறந்துவிட்டதா?",
        "no_account": "கணக்கு இல்லையா?",
        "register_here": "இங்கே பதிவு செய்யவும்",
        "demo_login_note": "டெமோ உள்நுழைவு — மொபைல்: <strong>9876543210</strong> · கடவுச்சொல்: <strong>demo1234</strong>",

        "register_heading": "ஆயிரக்கணக்கான விவசாயிகளுடன்<br>இணையுங்கள்.",
        "register_hero_text": "ஒரு நிமிடத்திற்குள் பதிவு செய்து, உங்கள் மாவட்டத்திற்கேற்ற AI பரிந்துரைகளைப் பெறுங்கள்.",
        "register_title": "புதிய கணக்கை உருவாக்கவும்",
        "register_subtitle": "விவசாயியாக பதிவு செய்யவும்",
        "label_name": "முழு பெயர்",
        "label_preferred_crop": "விருப்பமான பயிர்",
        "label_email": "மின்னஞ்சல் (விருப்பத்தேர்வு)",
        "label_district": "மாவட்டம்",
        "label_farm_size": "பண்ணை அளவு (ஏக்கரில்)",
        "label_confirm_password": "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
        "placeholder_name": "உங்கள் முழு பெயரை உள்ளிடவும்",
        "placeholder_email": "உங்கள் மின்னஞ்சலை உள்ளிடவும்",
        "placeholder_mobile_reg": "மொபைல் எண்ணை உள்ளிடவும்",
        "placeholder_farm_size": "பண்ணை அளவை உள்ளிடவும்",
        "placeholder_password_create": "கடவுச்சொல்லை உருவாக்கவும்",
        "placeholder_password_confirm": "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
        "select_crop_placeholder": "விருப்பமான பயிரைத் தேர்ந்தெடுக்கவும்",
        "select_district_placeholder": "உங்கள் மாவட்டத்தைத் தேர்ந்தெடுக்கவும்",
        "already_account": "ஏற்கனவே கணக்கு உள்ளதா?",
        "login_here": "இங்கே உள்நுழையவும்",

        "forgot_heading": "கடவுச்சொல் மறந்துவிட்டதா?<br>கவலைப்பட வேண்டாம்.",
        "forgot_hero_text": "உங்கள் பதிவு செய்யப்பட்ட மொபைல் எண்ணை உள்ளிடவும், உங்கள் கணக்கை மீண்டும் அணுக உதவுவோம்.",
        "forgot_title": "கடவுச்சொல்லை மீட்டமைக்கவும்",
        "forgot_subtitle": "உங்கள் பதிவு செய்யப்பட்ட மொபைல் எண்ணுக்கு மீட்டமைப்பு இணைப்பை அனுப்புவோம்",
        "placeholder_mobile_registered": "பதிவு செய்யப்பட்ட மொபைல் எண்ணை உள்ளிடவும்",
        "btn_send_reset": "மீட்டமைப்பு இணைப்பை அனுப்பவும்",
        "remembered_password": "கடவுச்சொல் நினைவிருக்கிறதா?",
        "back_to_login": "உள்நுழைவுக்குத் திரும்பு",

        "welcome": "வணக்கம்",
        "district_label": "மாவட்டம்",
        "todays_weather": "இன்றைய வானிலை",
        "temperature": "வெப்பநிலை",
        "rainfall": "மழைப்பொழிவு",
        "humidity": "ஈரப்பதம்",
        "wind_speed": "காற்றின் வேகம்",
        "this_week": "இந்த வாரம்",
        "rainfall_forecast": "மழைப்பொழிவு முன்னறிவிப்பு",
        "next_7_days": "அடுத்த 7 நாட்கள் (மி.மீ)",
        "climate_alerts": "காலநிலை எச்சரிக்கைகள்",
        "view_all_alerts": "அனைத்து எச்சரிக்கைகளையும் காண்க",
        "temperature_trend": "வெப்பநிலை போக்கு",
        "quick_actions": "விரைவு செயல்கள்",

        "weather_forecast": "வானிலை முன்னறிவிப்பு",
        "day_forecast_for": "7-நாள் முன்னறிவிப்பு",
        "average": "சராசரி",
        "col_date": "தேதி",
        "col_weather": "வானிலை",
        "col_temp": "வெப்பநிலை (°C)",
        "col_rainfall": "மழை (மி.மீ)",
        "col_humidity": "ஈரப்பதம் (%)",
        "col_wind": "காற்று (கிமீ/மணி)",
        "forecast_table_title": "7 நாள் வானிலை முன்னறிவிப்பு",

        "crop_recommendation": "பயிர் பரிந்துரை",
        "rec_subtitle": "AI அடிப்படையிலான பயிர் நாட்காட்டி பரிந்துரையைப் பெற விவரங்களைத் தேர்ந்தெடுக்கவும்",
        "select_district": "மாவட்டத்தைத் தேர்ந்தெடுக்கவும்",
        "select_crop": "பயிரைத் தேர்ந்தெடுக்கவும்",
        "select_season": "பருவத்தைத் தேர்ந்தெடுக்கவும்",
        "analyze_btn": "பகுப்பாய்வு செய்து பரிந்துரையைப் பெறவும்",
        "analyzing": "காலநிலை தரவு பகுப்பாய்வு செய்யப்படுகிறது...",
        "historical_data": "வரலாற்று தரவு பகுப்பாய்வு",
        "ai_prediction_model": "AI முன்கணிப்பு மாதிரி",
        "smart_calendar": "ஸ்மார்ட் பயிர் நாட்காட்டி",
        "about_rec_title": "இந்த பரிந்துரையைப் பற்றி:",
        "about_rec_text": "எங்கள் AI மாதிரி வரலாற்று வானிலை தரவு, பருவமழை முறைகள் மற்றும் மண் நிலைமைகளை பகுப்பாய்வு செய்து, நீங்கள் தேர்ந்தெடுத்த பயிர் மற்றும் பருவத்திற்கான சிறந்த விதைப்பு காலத்தை பரிந்துரைக்கிறது.",

        "ai_result_title": "AI பரிந்துரை முடிவு",
        "ai_result_subtitle": "காலநிலை பகுப்பாய்வு மற்றும் ML முன்கணிப்பின் அடிப்படையில்",
        "recommended_crop": "பரிந்துரைக்கப்பட்ட பயிர்",
        "season": "பருவம்",
        "recommended_window": "பரிந்துரைக்கப்பட்ட காலம்",
        "best_sowing_date": "சிறந்த விதைப்பு தேதி",
        "weather_prediction": "வானிலை முன்கணிப்பு",
        "expected_rainfall": "எதிர்பார்க்கப்படும் மழை",
        "avg_temperature": "சராசரி வெப்பநிலை",
        "risk_assessment": "அபாய மதிப்பீடு",
        "drought_risk": "வறட்சி அபாயம்",
        "flood_risk": "வெள்ள அபாயம்",
        "overall_risk": "மொத்த அபாயம்",
        "model_confidence": "மாதிரி நம்பகத்தன்மை",
        "high_confidence": "உயர் நம்பகத்தன்மை",
        "ai_suggestions": "AI பரிந்துரைகள்",
        "download_pdf": "PDF அறிக்கையை பதிவிறக்கவும்",
        "add_to_calendar": "எனது நாட்காட்டியில் சேர்க்கவும்",
        "risk_low": "குறைவு",
        "risk_moderate": "மிதமானது",
        "risk_high": "அதிகம்",

        "crop_calendar_title": "பயிர் நாட்காட்டி",
        "based_on_latest": "உங்கள் சமீபத்திய பரிந்துரையின் அடிப்படையில்",
        "no_rec_yet": "இன்னும் பரிந்துரை இல்லை",
        "next": "அடுத்து",
        "recommended_days": "பரிந்துரைக்கப்பட்ட நாட்கள்",
        "acceptable_days": "ஏற்கத்தக்க நாட்கள்",
        "high_risk_days": "அதிக ஆபத்து நாட்கள்",
        "download_calendar_pdf": "நாட்காட்டி PDF பதிவிறக்கவும்",
        "save_recommendation": "பரிந்துரையை சேமிக்கவும்",
        "saved": "சேமிக்கப்பட்டது",
        "no_rec_generated": "நீங்கள் இன்னும் பயிர் பரிந்துரையை உருவாக்கவில்லை.",
        "get_one_now": "இப்போது பெறுங்கள்",

        "notifications_title": "அறிவிப்புகள்",
        "notifications_subtitle": "முக்கிய எச்சரிக்கைகள் மற்றும் பரிந்துரைகளுடன் புதுப்பித்த நிலையில் இருங்கள்",
        "tab_all": "அனைத்தும்",
        "tab_weather": "வானிலை எச்சரிக்கைகள்",
        "tab_monsoon": "பருவமழை எச்சரிக்கைகள்",
        "tab_sowing": "விதைப்பு நினைவூட்டல்கள்",
        "tab_system": "கணினி எச்சரிக்கைகள்",
        "no_notifications": "இன்னும் அறிவிப்புகள் இல்லை.",

        "farmer_profile": "விவசாயி சுயவிவரம்",
        "profile_subtitle": "உங்கள் தனிப்பட்ட தகவல் மற்றும் விருப்பங்களை நிர்வகிக்கவும்",
        "edit_profile": "சுயவிவரத்தைத் திருத்தவும்",
        "cancel": "ரத்து செய்",
        "farm_size": "பண்ணை அளவு",
        "preferred_crop": "விருப்பமான பயிர்",
        "member_since": "உறுப்பினரான தேதி",
        "save_changes": "மாற்றங்களை சேமிக்கவும்",
        "recent_recommendations": "சமீபத்திய பரிந்துரைகள்",
        "no_recs_generated": "இதுவரை பரிந்துரைகள் உருவாக்கப்படவில்லை.",
        "view": "காண்க",
        "acres": "ஏக்கர்",
        "no_email_added": "மின்னஞ்சல் சேர்க்கப்படவில்லை",
    },
}


# ---- Localized display names for dropdowns / labels (values sent to the
#      backend stay in English so app.py logic never has to change) ----
DISTRICT_TA = {
    "Chennai": "சென்னை",
    "Thanjavur": "தஞ்சாவூர்",
    "Madurai": "மதுரை",
    "Coimbatore": "கோயம்புத்தூர்",
    "Trichy": "திருச்சி",
    "Salem": "சேலம்",
    "Tirunelveli": "திருநெல்வேலி",
    "Erode": "ஈரோடு",
}

CROP_TA = {
    "Rice": "நெல்",
    "Groundnut": "நிலக்கடலை",
    "Cotton": "பருத்தி",
    "Sugarcane": "கரும்பு",
    "Maize": "சோளம்",
    "Millets": "சிறுதானியங்கள்",
    "Banana": "வாழை",
}

SEASON_TA = {
    "Kuruvai": "குறுவை",
    "Samba": "சம்பா",
    "Navarai": "நவரை",
}


def translate(key, lang="en"):
    """Look up `key` in the given language, falling back to English,
    then to the raw key itself so nothing ever renders blank."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))


def translate_district(name, lang="en"):
    return DISTRICT_TA.get(name, name) if lang == "ta" else name


def translate_crop(name, lang="en"):
    return CROP_TA.get(name, name) if lang == "ta" else name


def translate_season(name, lang="en"):
    return SEASON_TA.get(name, name) if lang == "ta" else name
