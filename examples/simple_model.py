"""Simple Pydantic model for testing."""

from pydantic import BaseModel


class Book(BaseModel):
    """A simple book model."""

    title: str
    author: str
    year: int
    isbn: str
