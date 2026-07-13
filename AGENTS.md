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
Vite proxies `/api` to `http://127.0.0.1:5000`. Frontend runs on port 3000, backend on 5000.

## Build & Deploy

**Docker (production):**
```bash
docker build . -t tw/meetingroom
docker compose up -d
```
Single container: nginx serves frontend static files + proxies `/api/` to Flask on 127.0.0.1:5000.

**Production services:** nginx (port 80) + Flask (port 5000 internal).

## Key Config

- `backend/config.yaml` — server port, DB path, JWT secrets, upload settings
- `backend/config.py` — loads YAML into Flask Config class
- `frontend/vite.config.js` — dev server port and API proxy

## Database

SQLite at `database/meeting_room.db`. Auto-created on first run. Schema migrations happen inline in `backend/app.py:migrate_db()` — no migration tool.

**Models:** User, Room, Booking, SystemBooking, LoginLog (see `backend/models.py`)

## API Routes

All under `/api/`, registered as Flask blueprints in `backend/app.py`:
- `routes/auth.py` — login, JWT auth
- `routes/users.py` — user CRUD (admin)
- `routes/rooms.py` — room management
- `routes/bookings.py` — booking CRUD
- `routes/system_bookings.py` — recurring system bookings

## Auth

JWT-based (`flask-jwt-extended`). Token in Authorization header. Admin users have `is_admin=True`.

## Frontend Structure

- `src/views/` — Vue pages (Login, Dashboard, Booking, AdminBookings, UserManage, RoomManage, etc.)
- `src/api/` — Axios request modules (auth, users, rooms, bookings)
- `src/router/` — Vue Router config
- `src/store/` — Pinia state management

## Gotchas

- Database and uploads are gitignored — first run creates them fresh
- No test suite exists
- `config.yaml` contains hardcoded JWT secrets (not env-var based)
- Upload limit: 50MB (app.py) but config.yaml says 100MB — app.py wins
- Admin password is randomly generated on first run and printed to stdout
