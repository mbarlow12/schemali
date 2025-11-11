# Schemali

A CLI tool for generating JSON schemas from Pydantic models.

## Features

- Load one or more Python modules containing Pydantic models
- Automatically discover all Pydantic models in each module
- Generate JSON schemas compliant with JSON Schema specification
- Write schemas to individual files
- Support for nested models and complex field types
- Customizable output directory and JSON formatting

## Installation

### From source

```bash
pip install -e .
```

### Dependencies

- Python >= 3.8
- pydantic >= 2.0.0

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

### Combined Options

```bash
schemali user.py product.py -o schemas/ --indent 4 -v
```

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
```

Running:

```bash
schemali models.py -v
```

Output:

```
Loading module: /path/to/models.py
Found 1 Pydantic model(s): ['User']
  ✓ User -> /current/dir/User.schema.json
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

## Help

For more information:

```bash
schemali --help
```

## License

MIT License - see LICENSE file for details.
