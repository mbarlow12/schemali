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
        assert '    "title"' in content

    def test_write_consolidated_schema(self, sample_model_file, temp_dir):
        """Test writing a consolidated schema file with all models."""
        writer = SchemaWriter(output_dir=temp_dir)
        module = writer.load_module_from_path(sample_model_file)
        models = writer.discover_pydantic_models(module)

        schema_path = writer.write_consolidated_schema(models)

        assert schema_path.exists()
        assert schema_path.name == "schemas.json"

        # Verify schema content
        with open(schema_path) as f:
            schema = json.load(f)

        # Check JSON Schema 2020-12 format
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert "$defs" in schema
        assert "title" in schema
        assert "description" in schema

        # Check that all models are in $defs
        assert "User" in schema["$defs"]
        assert "Product" in schema["$defs"]

        # Verify model schemas in $defs
        user_schema = schema["$defs"]["User"]
        assert user_schema["title"] == "User"
        assert "properties" in user_schema
        assert "id" in user_schema["properties"]
        assert "name" in user_schema["properties"]

        product_schema = schema["$defs"]["Product"]
        assert product_schema["title"] == "Product"
        assert "properties" in product_schema
        assert "title" in product_schema["properties"]
        assert "price" in product_schema["properties"]

    def test_write_consolidated_schema_custom_path(self, sample_model_file, temp_dir):
        """Test writing consolidated schema with custom path."""
        writer = SchemaWriter(output_dir=temp_dir)
        module = writer.load_module_from_path(sample_model_file)
        models = writer.discover_pydantic_models(module)

        custom_path = temp_dir / "custom_schemas.json"
        schema_path = writer.write_consolidated_schema(models, output_path=custom_path)

        assert schema_path == custom_path
        assert schema_path.exists()

        with open(schema_path) as f:
            schema = json.load(f)

        assert "$defs" in schema
        assert len(schema["$defs"]) == 2

    def test_write_consolidated_schema_custom_indent(self, sample_model_file, temp_dir):
        """Test writing consolidated schema with custom indentation."""
        writer = SchemaWriter(output_dir=temp_dir)
        module = writer.load_module_from_path(sample_model_file)
        models = writer.discover_pydantic_models(module)

        schema_path = writer.write_consolidated_schema(models, indent=4)

        content = schema_path.read_text()
        # Check that indentation is 4 spaces
        assert '    "$schema"' in content
        assert '    "$defs"' in content

    def test_write_consolidated_schema_empty_models(self, temp_dir):
        """Test writing consolidated schema with no models."""
        writer = SchemaWriter(output_dir=temp_dir)
        schema_path = writer.write_consolidated_schema([])

        assert schema_path.exists()

        with open(schema_path) as f:
            schema = json.load(f)

        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert "$defs" in schema
        assert len(schema["$defs"]) == 0
