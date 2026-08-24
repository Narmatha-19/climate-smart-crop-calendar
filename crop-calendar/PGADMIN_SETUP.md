# Connecting the App to PostgreSQL via pgAdmin

The app moved from SQLite (`database/crop_calendar.db`) to PostgreSQL. This walks through
creating the database in pgAdmin, telling the app how to reach it, and running it end to end
— then how to open it as an installable app on your Android phone.

Nothing in the app's features, pages, or content changed for this — this is purely a backend
swap. See `PROJECT_CHANGELOG.md` for what "unrelated" work happened earlier in the project.

---

## 1. Create the database in pgAdmin

1. Open **pgAdmin** (the desktop app you already installed).
2. In the left tree, expand **Servers → PostgreSQL 18** (or whatever your server is named).
   You'll be asked for the **master password** you set when you installed PostgreSQL — this
   is the password for the `postgres` superuser account. If you don't remember it, see
   [Troubleshooting](#troubleshooting) below.
3. Right-click **Databases → Create → Database…**
4. Set:
   - **Database name:** `crop_calendar`
   - **Owner:** `postgres` (default is fine)
5. Click **Save**.

That's it — the app creates all its own tables (`farmers`, `recommendations`, `notifications`)
automatically the first time it runs, the same way it did with SQLite. You don't need to run
any `CREATE TABLE` SQL yourself in pgAdmin.

---

## 2. Tell the app how to connect

The app reads its database credentials from a `.env` file (not committed to git, so your
password never ends up in source control).

1. In the project folder (`crop-calendar/`), copy `.env.example` to a new file named `.env`.
2. Open `.env` and fill in the password you used for the `postgres` user in step 1:

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=crop_calendar
   DB_USER=postgres
   DB_PASSWORD=your_actual_postgres_password
   ```

   If you'd rather not use the `postgres` superuser for the app, you can create a dedicated
   role instead — right-click **Login/Group Roles → Create → Login/Group Role…** in pgAdmin,
   give it a name/password, tick **Can login?** on the *Privileges* tab, then grant it access:
   right-click `crop_calendar` → **Properties → Security** → add the role with **ALL**
   privileges. Use that role's name/password in `.env` instead.

---

## 3. What changed in the code (for reference)

You don't need to do anything here — just context for what the migration touched:

| File | Change |
|---|---|
| `db.py` *(new)* | Connects to PostgreSQL via `psycopg2`, reading host/port/name/user/password from the environment variables above. Wraps the connection so the rest of the app can keep calling `conn.execute(sql, params)` exactly like it did with SQLite. |
| `app.py` | `import sqlite3` → `from db import get_db`; loads `.env` via `python-dotenv` on startup; the `CREATE TABLE` schema now uses PostgreSQL syntax (`SERIAL PRIMARY KEY` instead of `INTEGER PRIMARY KEY AUTOINCREMENT`, `TO_CHAR(CURRENT_TIMESTAMP, ...)` instead of `datetime('now')`); the two spots that used SQLite's `cursor.lastrowid` / `last_insert_rowid()` now use PostgreSQL's `INSERT ... RETURNING id` instead. |
| `requirements.txt` | Added `psycopg2-binary` and `python-dotenv`. |
| `.env.example` *(new)* | Template for `.env` — copy it, don't edit it directly. |
| `.gitignore` *(new)* | Added so `.env` (your real password) never gets committed. |

No template, route, or feature logic changed — every page's HTML/CSS/JS content is exactly
what it was before.

---

## 4. Install dependencies & run

```bash
cd crop-calendar
pip install -r requirements.txt
python app.py
```

On first run you should see the app start normally, and pgAdmin will now show three new
tables under `crop_calendar → Schemas → public → Tables` (`farmers`, `recommendations`,
`notifications`) with the demo farmer already seeded (mobile `9876543210`, password
`demo1234`) — refresh the tree in pgAdmin if you don't see them right away.

---

## 5. Opening it on your Android phone (same WiFi)

Flask's dev server is already told to listen on all network interfaces
(`app.run(host="0.0.0.0", ...)`), so any device on the same WiFi as your laptop can reach it.

1. Find your laptop's local IP address:
   ```
   ipconfig
   ```
   Look for **IPv4 Address** under your active WiFi adapter — something like `192.168.1.42`.
2. On your phone (same WiFi network), open Chrome and go to:
   ```
   http://192.168.1.42:5000
   ```
   (using your laptop's actual IP from step 1).
3. You should see the same splash/login page as on your laptop.

### Installing it like an app

Tap Chrome's **⋮ menu → Add to Home screen**. It'll use the leaf icon and app name from
`static/manifest.json` and open full-screen, without the browser address bar, like a real app.

**One honest caveat:** full PWA behavior (the automatic "Install app" banner + offline page
caching via the service worker) requires either `https://` or `http://localhost` — browsers
treat a phone accessing your laptop's plain `http://192.168.x.x` LAN address as "not secure,"
so the service worker registration will silently fail there (the app still works fine, you
just won't get offline caching, and installing is a manual "Add to Home screen" tap instead
of an automatic banner). This is completely normal for local-network testing and totally fine
for a demo. If you want the full installable-with-offline-caching experience for your guide,
the easiest fix without deploying anywhere is a free HTTPS tunnel:

```bash
# one-time: download ngrok from ngrok.com, then:
ngrok http 5000
```

This gives you a temporary `https://something.ngrok-free.app` URL that tunnels straight to
your laptop's Flask server — open that URL on your phone instead, and the full "Install app"
banner + offline caching will work exactly as designed.

---

## Troubleshooting

**"I don't remember my postgres password."** In pgAdmin, right-click your server → **Properties → Connection** won't show the saved
password (pgAdmin masks it), but if pgAdmin can already connect to the server without
prompting you, that means it's cached — right-click the server → **Disconnect Server**, then
reconnect; if it *doesn't* prompt you for a password, pgAdmin has it saved and you can find it
in Windows Credential Manager, or simplest: reset it via `ALTER USER postgres WITH PASSWORD 'newpassword';` in pgAdmin's Query Tool once you're connected, then use that new password in `.env`.

**App shows a connection error on startup.** Double-check `.env` exists (not just
`.env.example`) and that `DB_PASSWORD` matches what pgAdmin uses to connect. Also confirm the
PostgreSQL Windows service is running: `services.msc` → look for `postgresql-x64-18`.

**Phone can't reach `http://192.168.x.x:5000`.** Confirm both devices are on the *same* WiFi
network (not phone on mobile data), and check Windows Firewall isn't blocking inbound
connections on port 5000 — Windows may prompt to allow this the first time you run `python app.py`; allow it for private networks.
