"""Configuration management for schemali using pydantic-settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)
from typing_extensions import override


class SchemaliConfig(BaseSettings):
    """Configuration for schemali CLI tool.

    Configuration can be loaded from:
    1. schemali.toml file in current directory
    2. .schemali.toml file in current directory
    3. ~/.config/schemali/config.toml
    4. Environment variables with SCHEMALI_ prefix
    5. Command-line arguments (highest priority)
    """

    model_config = SettingsConfigDict(
        toml_file=["schemali.toml", ".schemali.toml"],
        env_prefix="SCHEMALI_",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Output configuration
    output_dir: Optional[Path] = Field(
        default=None, description="Default output directory for schema files"
    )

    indent: int = Field(default=2, ge=0, le=8, description="JSON indentation spaces")

    # Behavior configuration
    verbose: bool = Field(default=False, description="Enable verbose output by default")

    # File naming configuration
    schema_suffix: str = Field(
        default=".schema.json", description="Suffix for generated schema files"
    )

    overwrite: bool = Field(default=True, description="Whether to overwrite existing schema files")

    # Single-file output configuration
    single_file: bool = Field(
        default=False, description="Generate a single consolidated schema file using $defs"
    )

    single_file_name: str = Field(
        default="schemas.json",
        description="Name of the single output file when single_file is enabled",
    )

    @classmethod
    def load_config(cls, config_file: Optional[Path] = None) -> "SchemaliConfig":
        """Load configuration from a specific file or default locations.

        Args:
            config_file: Optional path to a specific config file.

        Returns:
            Loaded configuration instance.
        """
        if config_file and config_file.exists():
            # Load from specific file
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib
                except ImportError:
                    tomllib = None

            if tomllib:
                with open(config_file, "rb") as f:
                    data = tomllib.load(f)
                    return cls(**data.get("tool", {}).get("schemali", {}))

        # Load from default locations (environment, default files, etc.)
        return cls()

    @override
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls), init_settings, env_settings)
