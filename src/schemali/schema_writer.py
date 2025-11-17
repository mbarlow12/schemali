"""Module for discovering Pydantic models and writing their JSON schemas."""

import importlib.util
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Type

try:
    from pydantic import BaseModel
except ImportError:
    raise ImportError("pydantic is required. Install it with: pip install pydantic")


class SchemaWriter:
    """Handles loading Python modules and extracting Pydantic model schemas."""

    def __init__(self, output_dir: Path = None):
        """
        Initialize the SchemaWriter.

        Args:
            output_dir: Directory where schema files will be written.
                       If None, uses current directory.
        """
        self.output_dir = output_dir or Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_module_from_path(self, module_path: Path) -> Any:
        """
        Dynamically load a Python module from a file path.

        Args:
            module_path: Path to the Python module file.

        Returns:
            The loaded module object.

        Raises:
            FileNotFoundError: If the module file doesn't exist.
            ImportError: If the module cannot be imported.
        """
        if not module_path.exists():
            raise FileNotFoundError(f"Module file not found: {module_path}")

        module_name = module_path.stem
        spec = importlib.util.spec_from_file_location(module_name, module_path)

        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

    def discover_pydantic_models(self, module: Any) -> List[Type[BaseModel]]:
        """
        Discover all Pydantic BaseModel subclasses in a module.

        Args:
            module: The Python module to inspect.

        Returns:
            List of Pydantic model classes found in the module.
        """
        models = []

        for name, obj in inspect.getmembers(module):
            # Check if it's a class, is a subclass of BaseModel,
            # and is not BaseModel itself
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseModel)
                and obj is not BaseModel
                and obj.__module__ == module.__name__
            ):
                models.append(obj)

        return models

    def write_schema(
        self, model: Type[BaseModel], output_path: Path = None, indent: int = 2
    ) -> Path:
        """
        Write a Pydantic model's JSON schema to a file.

        Args:
            model: The Pydantic model class.
            output_path: Custom output path for the schema file.
                        If None, uses output_dir/{model_name}.schema.json
            indent: Number of spaces for JSON indentation.

        Returns:
            Path to the written schema file.
        """
        if output_path is None:
            output_path = self.output_dir / f"{model.__name__}.schema.json"

        # Generate JSON schema
        schema = model.model_json_schema()

        # Write to file
        with open(output_path, "w") as f:
            json.dump(schema, f, indent=indent)

        return output_path

    def write_consolidated_schema(
        self,
        models: List[Type[BaseModel]],
        output_path: Path = None,
        indent: int = 2,
    ) -> Path:
        """
        Write all Pydantic models' schemas to a single file using JSON Schema 2020-12 format.

        This creates a consolidated schema file that uses $defs to define all models
        and conforms to the JSON Schema 2020-12 specification.

        Args:
            models: List of Pydantic model classes.
            output_path: Path for the consolidated schema file.
            indent: Number of spaces for JSON indentation.

        Returns:
            Path to the written schema file.
        """
        if output_path is None:
            output_path = self.output_dir / "schemas.json"

        # Build the consolidated schema structure
        consolidated_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": output_path.as_uri(),
            "title": "Consolidated Pydantic Models Schema",
            "description": "JSON Schema definitions for all Pydantic models",
            "$defs": {},
        }

        # Generate schema for each model and add to $defs
        for model in models:
            schema = model.model_json_schema(mode="serialization")

            # Remove the top-level $schema if present (we have one at the root)
            schema.pop("$schema", None)

            # Add to $defs with the model name as the key
            consolidated_schema["$defs"][model.__name__] = schema

        # Write to file
        with open(output_path, "w") as f:
            json.dump(consolidated_schema, f, indent=indent)

        return output_path

    def process_module(
        self, module_path: Path, indent: int = 2, verbose: bool = False
    ) -> Dict[str, Path]:
        """
        Process a Python module: load it, discover models, and write schemas.

        Args:
            module_path: Path to the Python module file.
            indent: Number of spaces for JSON indentation.
            verbose: Whether to print verbose output.

        Returns:
            Dictionary mapping model names to their schema file paths.
        """
        results = {}

        if verbose:
            print(f"Loading module: {module_path}")

        # Load the module
        module = self.load_module_from_path(module_path)

        # Discover Pydantic models
        models = self.discover_pydantic_models(module)

        if verbose:
            print(f"Found {len(models)} Pydantic model(s): {[m.__name__ for m in models]}")

        # Write schema for each model
        for model in models:
            schema_path = self.write_schema(model, indent=indent)
            results[model.__name__] = schema_path

            if verbose:
                print(f"  ✓ {model.__name__} -> {schema_path}")

        return results
