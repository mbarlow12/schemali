# Schemali

A modern CLI tool for generating JSON schemas from Pydantic models.

## Features

- 🚀 Load one or more Python modules containing Pydantic models
- 🔍 Automatically discover all Pydantic models in each module
- 📋 Generate JSON schemas compliant with JSON Schema specification
- 💾 Write schemas to individual files
- 🎨 Beautiful terminal output with colors and tables
- ⚙️ Flexible configuration via TOML files, environment variables, or CLI arguments
- 🧪 Comprehensive test coverage with pytest
- 🎯 Support for nested models and complex field types
- 🔧 Customizable output directory and JSON formatting

## Installation

### Using uv (recommended)

```bash
uv pip install schemali
```

### Using pip

```bash
pip install schemali
```

### From source

```bash
git clone https://github.com/mbarlow12/schemali.git
cd schemali
uv pip install -e ".[dev]"
```

## Dependencies

- Python >= 3.8
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- typer >= 0.9.0
- rich >= 13.0.0

## Quick Start

```bash
# Process a single module
schemali models.py

# Process multiple modules
schemali user.py product.py order.py

# Specify output directory
schemali models.py -o schemas/

# Use verbose output
schemali models.py -v
```

## Usage

### Basic Usage

Generate schemas from a single Python module:

```bash
schemali models.py
```

This will create `{ModelName}.schema.json` files in the current directory for each Pydantic model found.

### Multiple Modules

Process multiple modules at once:

```bash
schemali user.py product.py order.py
```

### Custom Output Directory

Specify where to write the schema files:

```bash
schemali models.py -o schemas/
# or
schemali models.py --output-dir schemas/
```

### Custom Indentation

Control JSON formatting (default is 2 spaces):

```bash
schemali models.py --indent 4
```

### Verbose Output

See detailed information about what's being processed:

```bash
schemali models.py -v
# or
schemali models.py --verbose
```

### Using a Configuration File

Create a `schemali.toml` configuration file:

```toml
[tool.schemali]
output_dir = "schemas"
indent = 4
verbose = false
schema_suffix = ".schema.json"
overwrite = true
```

Then run:

```bash
schemali models.py -c schemali.toml
```

### Environment Variables

You can also configure schemali using environment variables with the `SCHEMALI_` prefix:

```bash
export SCHEMALI_OUTPUT_DIR="schemas"
export SCHEMALI_INDENT=4
export SCHEMALI_VERBOSE=true

schemali models.py
```

### Combined Options

Command-line arguments override configuration file settings:

```bash
schemali user.py product.py -o schemas/ --indent 4 -v -c config.toml
```

## Configuration

Schemali uses a flexible configuration system powered by **pydantic-settings**. Configuration sources are prioritized as follows (highest to lowest):

1. Command-line arguments
2. Configuration file (TOML)
3. Environment variables (with `SCHEMALI_` prefix)
4. Default values

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_dir` | Path | current dir | Output directory for schema files |
| `indent` | int | 2 | JSON indentation spaces (0-8) |
| `verbose` | bool | false | Enable verbose output |
| `schema_suffix` | str | `.schema.json` | Suffix for generated schema files |
| `overwrite` | bool | true | Whether to overwrite existing files |

### Configuration File Locations

Schemali searches for configuration files in the following locations:

1. `./schemali.toml` (current directory)
2. `./.schemali.toml` (current directory, hidden)
3. `~/.config/schemali/config.toml` (user config directory)
4. Custom path via `-c/--config` flag

## Example

Given a Python module `models.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    """User model."""
    id: int
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: bool = True

class Product(BaseModel):
    """Product model."""
    id: int
    name: str
    price: float = Field(..., gt=0)
```

Running:

```bash
schemali models.py -v
```

Output:

```
Processing module: /path/to/models.py

┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Model   ┃ Schema File                          ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ User    │ /current/dir/User.schema.json        │
│ Product │ /current/dir/Product.schema.json     │
└─────────┴───────────────────────────────────────┘

✓ Complete! Generated 2 schemas
```

Generated `User.schema.json`:

```json
{
  "description": "User model.",
  "properties": {
    "id": {
      "title": "Id",
      "type": "integer"
    },
    "username": {
      "maxLength": 50,
      "minLength": 3,
      "title": "Username",
      "type": "string"
    },
    "email": {
      "title": "Email",
      "type": "string"
    },
    "age": {
      "anyOf": [
        {
          "maximum": 150,
          "minimum": 0,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Age"
    },
    "is_active": {
      "default": true,
      "title": "Is Active",
      "type": "boolean"
    }
  },
  "required": ["id", "username", "email"],
  "title": "User",
  "type": "object"
}
```

## Running as a Python Module

You can also run schemali as a Python module:

```bash
python -m schemali models.py
```

## Development

### Setup

We use **uv** for dependency management:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

### Code Quality

We use **Ruff** for linting and formatting:

```bash
# Check code
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Project Structure

```
schemali/
├── schemali/           # Main package
│   ├── __init__.py
│   ├── __main__.py     # Entry point
│   ├── cli.py          # CLI using Typer
│   ├── config.py       # Configuration with pydantic-settings
│   └── schema_writer.py # Core logic
├── tests/              # Test suite
│   ├── conftest.py     # Test fixtures
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_schema_writer.py
├── examples/           # Example models
├── pyproject.toml      # Project configuration
├── README.md
└── CLAUDE.md           # Developer documentation
```

## Technology Stack

- **Build System**: hatchling (for uv compatibility)
- **CLI Framework**: Typer (type-safe, modern CLI)
- **Configuration**: pydantic-settings (TOML + env vars)
- **Terminal Output**: Rich (beautiful formatting)
- **Testing**: pytest with coverage
- **Linting**: Ruff (fast Python linter)

## Help

For more information:

```bash
schemali --help
```

## Contributing

Contributions are welcome! Please see [CLAUDE.md](CLAUDE.md) for developer documentation.

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Run linter: `ruff check .`
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/mbarlow12/schemali)
- [Issue Tracker](https://github.com/mbarlow12/schemali/issues)
- [Changelog](https://github.com/mbarlow12/schemali/releases)
