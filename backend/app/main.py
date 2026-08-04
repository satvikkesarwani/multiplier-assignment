from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.database import engine, Base
from app.api.auth import router as auth_router
from app.api.preview import router as preview_router

from app.core.config import settings

# Import models so SQLAlchemy registers them before creating tables
import app.models.user
import app.models.preview



# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Preview API",
    description="A simple API for authentication and URL screenshot previews",
    version="1.0.0"
)

# Allow React frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve screenshot images as static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register route groups
app.include_router(auth_router)
app.include_router(preview_router)

@app.get("/")
def root():
    return {"message": "URL Preview API is running!"}
