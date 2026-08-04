import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = BACKEND_DIR / "url_preview.db"


class Settings:
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "development-only-secret-change-before-deployment",
    )

    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_DATABASE_PATH}",
    )

    FRONTEND_ORIGIN: str = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )


settings = Settings()