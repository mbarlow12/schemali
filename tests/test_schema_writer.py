"""Tests for schema_writer module."""

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from schemali.schema_writer import SchemaWriter


class TestSchemaWriter:
    """Test SchemaWriter class."""

    def test_init_default_output_dir(self):
        """Test initialization with default output directory."""
        writer = SchemaWriter()
        assert writer.output_dir == Path.cwd()

    def test_init_custom_output_dir(self, temp_dir):
        """Test initialization with custom output directory."""
        output_dir = temp_dir / "schemas"
        writer = SchemaWriter(output_dir=output_dir)
        assert writer.output_dir == output_dir
        assert output_dir.exists()

    def test_load_module_from_path(self, sample_model_file):
        """Test loading a Python module from file path."""
        writer = SchemaWriter()
        module = writer.load_module_from_path(sample_model_file)

        assert hasattr(module, "User")
        assert hasattr(module, "Product")
        assert issubclass(module.User, BaseModel)
        assert issubclass(module.Product, BaseModel)

    def test_load_module_from_path_not_found(self, temp_dir):
        """Test loading a non-existent module."""
        writer = SchemaWriter()
        non_existent = temp_dir / "does_not_exist.py"

        with pytest.raises(FileNotFoundError):
            writer.load_module_from_path(non_existent)

    def test_discover_pydantic_models(self, sample_model_file):
        """Test discovering Pydantic models in a module."""
        writer = SchemaWriter()
        module = writer.load_module_from_path(sample_model_file)
        models = writer.discover_pydantic_models(module)

        assert len(models) == 2
        model_names = {model.__name__ for model in models}
        assert model_names == {"User", "Product"}

    def test_discover_pydantic_models_empty(self, empty_model_file):
        """Test discovering models in a module with no Pydantic models."""
        writer = SchemaWriter()
        module = writer.load_module_from_path(empty_model_file)
        models = writer.discover_pydantic_models(module)

        assert len(models) == 0

    def test_write_schema(self, temp_dir):
        """Test writing a schema to file."""

        class TestModel(BaseModel):
            """Test model."""
            name: str
            value: int

        writer = SchemaWriter(output_dir=temp_dir)
        schema_path = writer.write_schema(TestModel)

        assert schema_path.exists()
        assert schema_path.name == "TestModel.schema.json"

        # Verify schema content
        with open(schema_path) as f:
            schema = json.load(f)

        assert schema["title"] == "TestModel"
        assert "name" in schema["properties"]
        assert "value" in schema["properties"]

    def test_write_schema_custom_indent(self, temp_dir):
        """Test writing schema with custom indentation."""

        class TestModel(BaseModel):
            name: str

        writer = SchemaWriter(output_dir=temp_dir)
        schema_path = writer.write_schema(TestModel, indent=4)

        content = schema_path.read_text()
        # Check that indentation is 4 spaces
        assert "    \"title\"" in content

    def test_process_module(self, sample_model_file, temp_dir):
        """Test processing a complete module."""
        writer = SchemaWriter(output_dir=temp_dir)
        results = writer.process_module(sample_model_file, verbose=False)

        assert len(results) == 2
        assert "User" in results
        assert "Product" in results

        # Verify files were created
        assert results["User"].exists()
        assert results["Product"].exists()

        # Verify schema content
        with open(results["User"]) as f:
            user_schema = json.load(f)

        assert user_schema["title"] == "User"
        assert "id" in user_schema["properties"]
        assert "name" in user_schema["properties"]
        assert "email" in user_schema["properties"]

    def test_process_module_verbose(self, sample_model_file, temp_dir, capsys):
        """Test processing module with verbose output."""
        writer = SchemaWriter(output_dir=temp_dir)
        results = writer.process_module(sample_model_file, verbose=True)

        captured = capsys.readouterr()
        assert "Loading module" in captured.out
        assert "Found 2 Pydantic model(s)" in captured.out
        assert "User" in captured.out
        assert "Product" in captured.out
