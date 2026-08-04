from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- Request Schemas ---

class PreviewCreateRequest(BaseModel):
    url: str  # The URL to generate a preview for

# --- Response Schemas ---

class PreviewResponse(BaseModel):
    id: int
    url: str
    screenshot_path: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
