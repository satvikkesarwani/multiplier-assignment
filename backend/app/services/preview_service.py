from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.screenshot import normalize_url, take_screenshot
from app.models.preview import Preview
from app.models.user import User


async def create_preview(db: Session, url: str, user: User) -> Preview:
    """Capture the URL and save a preview owned by the current user."""
    try:
        normalized_url = normalize_url(url)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    screenshot_path = await take_screenshot(normalized_url)

    if screenshot_path is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The website preview could not be generated. "
                "The site may be unavailable or blocking automated browsers."
            ),
        )

    preview = Preview(
        url=normalized_url,
        screenshot_path=screenshot_path,
        user_id=user.id,
    )

    try:
        db.add(preview)
        db.commit()
        db.refresh(preview)
        return preview

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The preview was generated but could not be saved.",
        )


def get_user_previews(db: Session, user: User) -> List[Preview]:
    """Return the current user's previews, newest first."""
    return (
        db.query(Preview)
        .filter(Preview.user_id == user.id)
        .order_by(Preview.created_at.desc())
        .all()
    )