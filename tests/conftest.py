"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_model_file(temp_dir):
    """Create a sample Python file with Pydantic models."""
    content = '''"""Sample models for testing."""

from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    """User model."""
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: Optional[int] = Field(None, ge=0, le=150)

class Product(BaseModel):
    """Product model."""
    id: int
    title: str
    price: float = Field(..., gt=0)
'''

    model_file = temp_dir / "test_models.py"
    model_file.write_text(content)
    return model_file


@pytest.fixture
def empty_model_file(temp_dir):
    """Create a Python file with no Pydantic models."""
    content = '''"""Module with no models."""

def some_function():
    pass

class RegularClass:
    pass
'''

    model_file = temp_dir / "no_models.py"
    model_file.write_text(content)
    return model_file


@pytest.fixture
def config_file(temp_dir):
    """Create a sample configuration file."""
    content = '''[tool.schemali]
output_dir = "schemas"
indent = 4
verbose = false
schema_suffix = ".schema.json"
overwrite = true
'''

    config_file = temp_dir / "schemali.toml"
    config_file.write_text(content)
    return config_file
