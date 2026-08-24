# Deploying to Render — so farmers can use it from anywhere

This puts the app on a real server that's online all the time, at a permanent public URL, so
any farmer can open it on their own mobile data or WiFi — no shared network with you or each
other required. This is separate from your local setup: your laptop's pgAdmin/PostgreSQL
keeps working for local development exactly as before; Render gets its own database.

`render.yaml` (at the repo root) already describes everything Render needs to build: the web
service and a managed PostgreSQL database, wired together automatically. You just need to
point Render at the repo.

---

## 1. Push the code to GitHub

Render deploys from your GitHub repo (`Narmatha-19/climate-smart-crop-calendar`, already
linked as `origin`). There's a lot of uncommitted work from this session that needs to be
committed and pushed first — **tell me when you're ready for that** and I'll prepare the
commit for your review before pushing anything (pushing to a shared repo is something I check
with you on, not something I do silently).

---

## 2. Create a Render account

1. Go to **render.com** → **Get Started** → sign up (GitHub sign-in is easiest since it can
   see your repos directly).
2. No credit card needed for the free tier used here.

---

## 3. Deploy the Blueprint

1. In the Render dashboard: **New +** → **Blueprint**.
2. Connect your GitHub account if prompted, then select the
   `climate-smart-crop-calendar` repo.
3. Render finds `render.yaml` automatically and shows a preview: one **web service**
   (`crop-calendar`) and one **PostgreSQL database** (`crop-calendar-db`).
4. Click **Apply** / **Create**.

Render will:
- Provision the PostgreSQL database first
- Build the web service (`pip install -r requirements.txt`, from inside `crop-calendar/`)
- Start it with `gunicorn app:app`
- Wire the database's host/port/name/user/password into the web service automatically as
  `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD` — the exact same variable names
  `db.py` already reads from your local `.env`, so no code changes were needed for this part.

First build takes a few minutes (installing pandas/scikit-learn/xgboost isn't instant). Watch
the **Logs** tab in the Render dashboard — you're looking for `Serving Flask app` (or
gunicorn's equivalent "Booting worker" lines) with no errors.

---

## 4. Get your public URL

Once it's live, Render shows a URL like:

```
https://crop-calendar.onrender.com
```

That's it — that's the link. Open it on any phone, on any network, anywhere. Same demo
farmer login works (`9876543210` / `demo1234`), and the database behind it is the one Render
just created — separate from your laptop's local one, and it persists (survives restarts).

---

## 5. Installing it on a farmer's phone

Same as before, just with a real HTTPS URL instead of a LAN IP — and this time it's the
**real thing**, not the local-network workaround:

1. Open `https://crop-calendar.onrender.com` in Chrome (Android) or Safari (iPhone).
2. Chrome: you should see an automatic **"Install app"** banner (this works properly now,
   unlike the local `http://192.168.x.x` case, because this is real HTTPS). Tap it — or use
   the ⋮ menu → **Add to Home screen** if the banner doesn't appear.
3. It installs with the leaf icon, opens full-screen, no browser address bar.

Share the URL itself however reaches your farmers — a WhatsApp message, an SMS, a printed QR
code pointing at the link, through a local agriculture office, etc. That's a distribution
choice for you to make; I can generate a QR code for the URL if that'd help once it's live.

---

## Things worth knowing about the free tier

- **Cold starts:** Render's free web services "spin down" after ~15 minutes of no traffic.
  The next request wakes it back up, but that first request can take 30-60 seconds. Not a bug
  — just how the free tier works. Fine for a student project; a paid plan removes this if you
  ever need it to stay always-instant.
- **Free database limits:** Render's free PostgreSQL tier has a storage cap and (on some plan
  versions) expires after 90 days unless upgraded — completely fine for a project/demo
  lifetime, just not meant as permanent production infrastructure.
- **Weather calls still work the same:** `models/weather_utils.py` calls the public
  Open-Meteo API directly from wherever the app is running, so live weather works identically
  on Render as it did locally.

---

## What's already done vs. what needs your action

| Step | Status |
|---|---|
| `render.yaml` blueprint (web service + database config) | ✅ Done |
| `requirements.txt` has `gunicorn` for production serving | ✅ Done |
| `app.py`: tables now created on import (works under gunicorn, not just `python app.py`) | ✅ Done |
| `app.py`: debug mode forced off in production (was a real security risk on a public URL) | ✅ Done |
| Commit & push this session's changes to GitHub | ⏳ Waiting on your go-ahead |
| Create Render account | ⏳ You |
| Click "Apply" on the Blueprint | ⏳ You (I can't create accounts/click through Render's dashboard on your behalf) |
