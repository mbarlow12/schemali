"""Tests for configuration module."""

from pathlib import Path

import pytest

from schemali.config import SchemaliConfig


class TestSchemaliConfig:
    """Test SchemaliConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SchemaliConfig()

        assert config.output_dir is None
        assert config.indent == 2
        assert config.verbose is False
        assert config.schema_suffix == ".schema.json"
        assert config.overwrite is True
        assert config.single_file is False
        assert config.single_file_name == "schemas.json"

    def test_config_with_custom_values(self):
        """Test configuration with custom values."""
        config = SchemaliConfig(
            output_dir=Path("schemas"),
            indent=4,
            verbose=True,
        )

        assert config.output_dir == Path("schemas")
        assert config.indent == 4
        assert config.verbose is True

    def test_config_indent_validation(self):
        """Test that indent is validated within range."""
        # Valid indents
        config = SchemaliConfig(indent=0)
        assert config.indent == 0

        config = SchemaliConfig(indent=8)
        assert config.indent == 8

        # Invalid indents
        with pytest.raises(Exception):  # Pydantic validation error
            SchemaliConfig(indent=-1)

        with pytest.raises(Exception):
            SchemaliConfig(indent=9)

    def test_load_config_default(self):
        """Test loading configuration with defaults."""
        config = SchemaliConfig.load_config()

        assert config.output_dir is None
        assert config.indent == 2
        assert config.verbose is False

    def test_config_from_env_vars(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("SCHEMALI_INDENT", "4")
        monkeypatch.setenv("SCHEMALI_VERBOSE", "true")

        config = SchemaliConfig()

        assert config.indent == 4
        assert config.verbose is True

    def test_schema_suffix_customization(self):
        """Test customizing the schema file suffix."""
        config = SchemaliConfig(schema_suffix=".json")
        assert config.schema_suffix == ".json"

        config = SchemaliConfig(schema_suffix="-schema.json")
        assert config.schema_suffix == "-schema.json"

    def test_single_file_config(self):
        """Test single file configuration options."""
        config = SchemaliConfig(single_file=True)
        assert config.single_file is True
        assert config.single_file_name == "schemas.json"

        config = SchemaliConfig(single_file=True, single_file_name="all-models.json")
        assert config.single_file is True
        assert config.single_file_name == "all-models.json"

    def test_single_file_from_env_vars(self, monkeypatch):
        """Test loading single file config from environment variables."""
        monkeypatch.setenv("SCHEMALI_SINGLE_FILE", "true")
        monkeypatch.setenv("SCHEMALI_SINGLE_FILE_NAME", "custom.json")

        config = SchemaliConfig()

        assert config.single_file is True
        assert config.single_file_name == "custom.json"
