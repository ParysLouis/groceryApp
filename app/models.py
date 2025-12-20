from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .database import Base


class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    quantity = Column(String(60), nullable=False, default="1")
    category = Column(String(60), nullable=True)
    purchased = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)