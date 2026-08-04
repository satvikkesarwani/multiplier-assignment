from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.preview import PreviewCreateRequest, PreviewResponse
from app.services.preview_service import create_preview, get_user_previews
from app.models.user import User

router = APIRouter(prefix="/api/previews", tags=["Previews"])

@router.post("/", response_model=PreviewResponse, status_code=201)
async def add_preview(
    data: PreviewCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a URL to capture its screenshot and save the preview."""
    preview = await create_preview(db, data.url, current_user)
    return preview

@router.get("/", response_model=List[PreviewResponse])
def list_previews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all saved previews for the logged-in user."""
    return get_user_previews(db, current_user)
