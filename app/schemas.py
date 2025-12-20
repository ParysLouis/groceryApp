from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GroceryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    quantity: str = Field(default="1", min_length=1, max_length=60)
    category: Optional[str] = Field(default=None, max_length=60)
    purchased: bool = False


class GroceryCreate(GroceryBase):
    pass


class GroceryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    quantity: Optional[str] = Field(default=None, min_length=1, max_length=60)
    category: Optional[str] = Field(default=None, max_length=60)
    purchased: Optional[bool] = None


class Grocery(GroceryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True