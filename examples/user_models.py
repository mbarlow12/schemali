"""Example Pydantic models for testing."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Address(BaseModel):
    """User address information."""

    street: str
    city: str
    state: str
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")
    country: str = "USA"


class User(BaseModel):
    """User model with various field types."""

    id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=50)
    email: str | None = None
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: bool = True
    created_at: datetime
    address: Optional[Address] = None
    tags: List[str] = Field(default_factory=list)


class Product(BaseModel):
    """Product model."""

    id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    in_stock: bool = True
    categories: List[str] = []
