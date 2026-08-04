from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PreviewCreateRequest(BaseModel):
    url: str = Field(
        min_length=3,
        max_length=2048,
        examples=["https://www.example.com"],
    )

    @field_validator("url")
    @classmethod
    def clean_url(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("URL cannot be empty")

        return value


class PreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    screenshot_path: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    user_id: int