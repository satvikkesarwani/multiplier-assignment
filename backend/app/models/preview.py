from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Preview(Base):
    __tablename__ = "previews"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    screenshot_path = Column(String, nullable=True)  # Path to the screenshot file
    title = Column(String, nullable=True)             # Optional page title
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key linking to the user who saved this preview
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="previews")
