from sqlalchemy.orm import Session
from typing import List
from app.models.preview import Preview
from app.models.user import User
from app.core.screenshot import take_screenshot

async def create_preview(db: Session, url: str, user: User) -> Preview:
    """Take a screenshot of the URL and save the preview to the database."""
    
    # Capture the screenshot (async operation using Playwright)
    screenshot_path = await take_screenshot(url)
    
    # Save preview record to DB
    preview = Preview(
        url=url,
        screenshot_path=screenshot_path,
        user_id=user.id
    )
    db.add(preview)
    db.commit()
    db.refresh(preview)
    return preview

def get_user_previews(db: Session, user: User) -> List[Preview]:
    """Retrieve all saved previews for a specific user, newest first."""
    return (
        db.query(Preview)
        .filter(Preview.user_id == user.id)
        .order_by(Preview.created_at.desc())
        .all()
    )
