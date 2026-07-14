# Meeting Room Booking System

## Architecture

Full-stack meeting room booking app. Vue 3 + Vite frontend, Flask + SQLAlchemy backend, SQLite database, nginx reverse proxy in Docker.

**Directory layout:**
- `backend/` — Flask API (app.py entrypoint, routes/, models.py, config.yaml)
- `frontend/` — Vue 3 SPA (Vite dev server, Element Plus UI, ECharts)
- `database/` — SQLite DB file (gitignored, created at runtime)
- `uploads/` — User-uploaded files (gitignored)

## Development

**Backend (Flask, port 5000):**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend (Vite dev server, port 3000):**
```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://10.19.1.168:5000` (hardcoded in `vite.config.js`). The target IP is not `localhost` — it's a remote/internal address. If developing locally, change this to your backend's actual IP.

CORS origin allowlist defaults to `localhost:3000,localhost:5173`. Override via env var:
```
CORS_ORIGINS=http://localhost:3000,http://10.19.1.168:3000 python app.py
```

## Build & Deploy

**Docker (multi-stage build):**
```bash
docker build . -t tw/meetingroom
docker save tw/meetingroom > mr.tar
docker compose up -d
```

Dockerfile uses two stages: `node:18-alpine` builds the frontend, `python:3.11-slim` runs Flask + nginx. Single container exposes port 80. nginx serves frontend static files and proxies `/api/` to Flask on 127.0.0.1:5000. Both nginx and Flask enforce a 50MB upload limit.

## Key Config

- `backend/config.yaml` — server port, DB path, JWT secrets, upload settings
- `backend/config.py` — loads YAML into Flask Config class; has PyInstaller compatibility (`sys._MEIPASS` check)
- `frontend/vite.config.js` — dev server port and API proxy target

## Database

SQLite at `database/meeting_room.db`. Auto-created on first run. Schema migrations happen inline in `backend/app.py:migrate_db()` — no migration tool.

**Models:** User, Room, Booking, SystemBooking, LoginLog (see `backend/models.py`)

## API Routes

All under `/api/`, registered as Flask blueprints in `backend/app.py`:
- `routes/auth.py` — login, JWT auth
- `routes/users.py` — user CRUD (admin)
- `routes/rooms.py` — room management
- `routes/bookings.py` — booking CRUD
- `routes/system_bookings.py` — recurring system bookings (weekday-based, 0=Sunday)

## Auth

JWT-based (`flask-jwt-extended`). Token in Authorization header. Admin users have `is_admin=True`.

## Frontend Structure

- `src/views/` — Vue pages (Login, Dashboard, Booking, AdminBookings, UserManage, RoomManage, etc.)
- `src/api/` — Axios request modules (auth, users, rooms, bookings)
- `src/router/` — Vue Router config
- `src/store/` — Pinia state management

## Gotchas

- Database and uploads are gitignored — first run creates them fresh
- No test suite, no linter, no typecheck, no formatter configured — `npm run` only offers `dev`, `build`, `preview`
- `config.yaml` contains hardcoded JWT secrets (not env-var based)
- Upload limit: 50MB in `app.py` and `nginx.conf`, but `config.yaml` says 100MB — app.py wins
- Admin password is randomly generated on first run and printed to stdout
- `frontend/src/asserts/` directory name is a typo (should be "assets") — don't "fix" it without updating all imports
- `requirements.txt` includes `openpyxl` for Excel export
