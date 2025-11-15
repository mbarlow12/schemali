# Schemali - Developer Documentation

This document provides information for developers working on the schemali project, including setup instructions, development workflows, and architectural decisions.

## Project Overview

Schemali is a CLI tool for generating JSON schemas from Pydantic models. It uses modern Python tooling and best practices to ensure maintainability and ease of development.

## Technology Stack

### Dependency Management & Build System

- **uv**: We use [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management
- **hatchling**: Build backend for the project (configured in `pyproject.toml`)

### Core Dependencies

- **pydantic >= 2.0.0**: Core dependency for working with Pydantic models
- **pydantic-settings >= 2.0.0**: Configuration management via TOML files and environment variables
- **typer >= 0.9.0**: Modern CLI framework with excellent type hints support
- **rich >= 13.0.0**: Beautiful terminal output with tables and colors

### Development Dependencies

- **pytest >= 7.0.0**: Testing framework
- **pytest-cov >= 4.0.0**: Code coverage reports
- **pytest-mock >= 3.0.0**: Mocking support for tests
- **ruff >= 0.1.0**: Fast Python linter and formatter

## Development Setup

### Initial Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in development mode with all dependencies
uv sync --all-groups

# Or install with specific dependency groups
uv sync --group dev
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_schema_writer.py

# Run tests with verbose output
pytest -v

# Run tests and generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Run linter
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .
```

## Architecture

### Module Structure

```
schemali/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for `python -m schemali`
├── cli.py               # CLI implementation using Typer
├── config.py            # Configuration management with pydantic-settings
└── schema_writer.py     # Core logic for schema generation
```

### Configuration System

The project uses **pydantic-settings** for configuration management, supporting multiple configuration sources with priority:

1. Command-line arguments (highest priority)
2. Configuration file (TOML)
3. Environment variables (with `SCHEMALI_` prefix)
4. Default values (lowest priority)

Configuration files are searched in the following order:
- `./schemali.toml`
- `./.schemali.toml`
- `~/.config/schemali/config.toml`

Example configuration file (`schemali.toml`):

```toml
[tool.schemali]
output_dir = "schemas"
indent = 4
verbose = false
schema_suffix = ".schema.json"
overwrite = true
single_file = false
single_file_name = "schemas.json"
```

### CLI Framework

We use **Typer** instead of argparse for several advantages:
- Automatic type validation from type hints
- Better help text generation
- Easier to test
- More maintainable code
- Excellent integration with Pydantic

### Schema Generation

The `SchemaWriter` class handles:
1. Dynamic module loading from file paths
2. Discovery of Pydantic `BaseModel` subclasses
3. JSON schema generation using Pydantic's built-in `model_json_schema()`
4. File output with configurable formatting

#### Single-File Mode

The tool supports generating a single consolidated schema file that conforms to JSON Schema 2020-12 specification:

- Uses `$defs` to define all model schemas
- Uses `$ref` constructs for referencing definitions
- Includes `$schema` pointing to `https://json-schema.org/draft/2020-12/schema`
- Configurable via `--single-file` CLI option or `single_file` config setting
- Custom filename via `--single-file-name` or `single_file_name` config setting

Example output structure:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "file:///path/to/schemas.json",
  "title": "Consolidated Pydantic Models Schema",
  "description": "JSON Schema definitions for all Pydantic models",
  "$defs": {
    "User": { ... },
    "Product": { ... }
  }
}
```

Usage:
```bash
# Generate single consolidated schema
schemali models.py --single-file

# With custom filename
schemali models.py --single-file --single-file-name all-schemas.json

# Multiple modules into single file
schemali user.py product.py order.py --single-file
```

## Testing Strategy

### Test Coverage Goals

- Maintain >85% code coverage
- All public APIs must have tests
- Critical paths must have integration tests

### Test Organization

- `tests/conftest.py`: Shared fixtures and configuration
- `tests/test_*.py`: Test modules mirroring source structure

### Writing Tests

```python
def test_feature(sample_model_file, temp_dir):
    """Test description."""
    # Arrange
    writer = SchemaWriter(output_dir=temp_dir)

    # Act
    result = writer.process_module(sample_model_file)

    # Assert
    assert len(result) > 0
```

## Release Process

1. Update version in `pyproject.toml` and `cli.py`
2. Run full test suite: `pytest`
3. Build package: `uv build`
4. Create git tag: `git tag v0.x.0`
5. Push with tags: `git push --tags`

## Common Tasks

### Adding a New Dependency

```bash
# Add runtime dependency
uv add <package>

# Add dev dependency to dev group
uv add --group dev <package>

# Add docs dependency to docs group
uv add --group docs <package>
```

All dependencies are managed in `pyproject.toml`:
- Runtime dependencies: `[project.dependencies]`
- Development dependencies: `[dependency-groups]` (following PEP 735)

### Adding a New CLI Command

1. Add new function in `cli.py` with `@app.command()` decorator
2. Use Typer's type hints for automatic validation
3. Add tests in `tests/test_cli.py`
4. Update README with usage examples

### Adding a New Configuration Option

1. Add field to `SchemaliConfig` in `config.py`
2. Add tests in `tests/test_config.py`
3. Update documentation in README and CLAUDE.md

## Code Style Guidelines

- Follow PEP 8 (enforced by Ruff)
- Use type hints everywhere
- Maximum line length: 100 characters
- Docstrings: Google style for modules, classes, and functions
- Imports: Sorted with isort (integrated in Ruff)

## Performance Considerations

- Dynamic module loading is done once per module
- Schema generation uses Pydantic's built-in methods (optimized in Rust)
- File I/O is minimal and done in a single write per schema

## Troubleshooting

### Tests Failing

```bash
# Clear pytest cache
rm -rf .pytest_cache
pytest --cache-clear

# Run with verbose output
pytest -vv
```

### Import Errors

```bash
# Reinstall in development mode
uv sync --all-groups
```

### Coverage Not Working

```bash
# Ensure dev dependencies (including pytest-cov) are installed
uv sync --group dev

# Run with explicit coverage
pytest --cov=schemali --cov-report=term-missing
```

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

## Contributing

When contributing to schemali:

1. Create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass: `pytest`
4. Run linter: `ruff check .`
5. Update documentation as needed
6. Submit a pull request

## Questions?

For questions or issues, please open an issue on the GitHub repository.
