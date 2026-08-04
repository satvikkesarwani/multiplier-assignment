# URL Preview App

A full-stack web application where users can sign up, log in, submit website URLs, and view visual previews (screenshots) of those websites.

## Tech Stack

- **Frontend**: React + Vite + React Router + Axios
- **Backend**: FastAPI + SQLAlchemy (SQLite) + Playwright

---

## Project Structure

```
url-preview-app/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers (auth.py, preview.py)
│   │   ├── core/          # Config, DB, security, screenshot logic
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic (auth_service, preview_service)
│   │   ├── static/        # Saved screenshot images
│   │   └── main.py        # FastAPI app entry point
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── api/           # Axios API client
    │   ├── components/    # Navbar, URLForm, PreviewCard, PreviewGrid, ProtectedRoute
    │   ├── context/       # AuthContext (JWT + user state)
    │   ├── pages/         # Login, Signup, Dashboard
    │   ├── App.jsx        # Routing
    │   └── index.css      # Global styles
    └── package.json
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

---

### Backend Setup

```bash
# 1. Go to the backend directory
cd backend

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser (Chromium for screenshots)
playwright install chromium

# 5. Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000  
Interactive API docs: http://localhost:8000/docs

---

### Frontend Setup

```bash
# Open a new terminal tab

# 1. Go to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the React dev server
npm run dev
```

The app will be available at: http://localhost:5173

---

## How It Works

1. **Signup** — Create an account at `/signup`
2. **Login** — Sign in at `/login`, receive a JWT token stored in localStorage
3. **Dashboard** — Enter any website URL (e.g., `https://www.justdial.com/...`)
4. **Screenshot** — FastAPI uses Playwright (headless Chromium) to capture a screenshot
5. **Storage** — The URL and screenshot path are saved in SQLite
6. **View** — All previously saved previews are displayed in a responsive grid

---

## API Endpoints

| Method | Endpoint             | Description                       | Auth Required |
|--------|----------------------|-----------------------------------|---------------|
| POST   | `/api/auth/signup`   | Register a new user               | No            |
| POST   | `/api/auth/login`    | Login, returns JWT token          | No            |
| GET    | `/api/auth/me`       | Get current user info             | Yes           |
| POST   | `/api/previews/`     | Submit URL, capture screenshot    | Yes           |
| GET    | `/api/previews/`     | Get all saved previews            | Yes           |

---

## Test URL

```
https://www.justdial.com/Hyderabad/Dr-Sarita-Rao-Tx-Hospitals-Near-Masjid-Uppal-Bus-Stand-Bharath-Nagar-Colony-Uppal/040PXX40-XX40-231215200040-Y2E1_BZDET
```

---

## Notes

- The database (`url_preview.db`) is created automatically on first run
- Screenshots are cached — the same URL won't be re-screenshotted
- The Vite dev server proxies `/api` and `/static` requests to the FastAPI backend
