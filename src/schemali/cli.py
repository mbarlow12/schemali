"""Command-line interface for schemali using Typer."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import SchemaliConfig
from .schema_writer import SchemaWriter

app = typer.Typer(
    name="schemali",
    help="Generate JSON schemas from Pydantic models",
    add_completion=False,
)

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print("schemali version 0.1.0")
        raise typer.Exit()


@app.command()
def main(
    modules: List[Path] = typer.Argument(
        ...,
        help="Python module file(s) containing Pydantic models",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output-dir",
        help="Output directory for schema files (default: current directory)",
    ),
    indent: Optional[int] = typer.Option(
        None,
        "--indent",
        min=0,
        max=8,
        help="JSON indentation spaces (default: 2)",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Enable verbose output",
    ),
    single_file: bool = typer.Option(
        False,
        "--single-file",
        help="Generate a single consolidated schema file using JSON Schema 2020-12 $defs",
    ),
    single_file_name: Optional[str] = typer.Option(
        None,
        "--single-file-name",
        help="Name of the single output file (default: schemas.json)",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "-c",
        "--config",
        help="Path to configuration file",
        exists=True,
        dir_okay=False,
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Generate JSON schemas from Pydantic models.

    Examples:

        # Process a single module
        schemali models.py

        # Process multiple modules
        schemali models.py user.py product.py

        # Specify output directory
        schemali models.py -o schemas/

        # Custom indentation and verbose output
        schemali models.py --indent 4 -v

        # Generate a single consolidated schema file (JSON Schema 2020-12)
        schemali models.py --single-file

        # Single file with custom name
        schemali models.py --single-file --single-file-name all-schemas.json

        # Use a configuration file
        schemali models.py -c config.toml
    """
    try:
        # Load configuration
        config = SchemaliConfig.load_config(config_file)

        # Command-line arguments override config file
        if output_dir is not None:
            config.output_dir = output_dir
        if indent is not None:
            config.indent = indent
        if verbose:
            config.verbose = verbose
        if single_file:
            config.single_file = single_file
        if single_file_name is not None:
            config.single_file_name = single_file_name

        # Validate modules are Python files
        for module_path in modules:
            if module_path.suffix != ".py":
                console.print(
                    f"[yellow]Warning:[/yellow] {module_path} is not a Python file, skipping"
                )
                modules.remove(module_path)

        if not modules:
            console.print("[red]Error:[/red] No valid Python modules provided")
            raise typer.Exit(1)

        # Initialize schema writer
        writer = SchemaWriter(output_dir=config.output_dir)

        # Track results
        total_models = 0
        all_results = {}
        all_models = []

        # Process each module to discover models
        for module_path in modules:
            if config.verbose:
                console.print(f"\n[bold]Processing module:[/bold] {module_path}")

            # Load the module
            module = writer.load_module_from_path(module_path)

            # Discover Pydantic models
            models = writer.discover_pydantic_models(module)
            all_models.extend(models)

            if config.verbose:
                model_names = [m.__name__ for m in models]
                console.print(f"Found {len(models)} Pydantic model(s): {model_names}")

        total_models = len(all_models)

        # Generate schemas based on mode
        if config.single_file:
            # Single consolidated schema file
            output_path = config.output_dir or Path.cwd()
            if config.output_dir:
                output_path = Path(config.output_dir)
            else:
                output_path = Path.cwd()

            schema_file_path = output_path / config.single_file_name

            result_path = writer.write_consolidated_schema(
                all_models,
                output_path=schema_file_path,
                indent=config.indent,
            )

            if config.verbose:
                console.print(
                    f"\n[bold green]✓ Generated consolidated schema:[/bold green] {result_path}"
                )

            all_results["__consolidated__"] = result_path
        else:
            # Individual schema files for each model
            for model in all_models:
                schema_path = writer.write_schema(model, indent=config.indent)
                all_results[model.__name__] = schema_path

                if config.verbose:
                    console.print(f"  ✓ {model.__name__} -> {schema_path}")

        # Display summary
        if total_models == 0:
            console.print("[yellow]No Pydantic models found in the provided modules[/yellow]")
            raise typer.Exit(0)

        if not config.verbose:
            if config.single_file:
                # Single file output
                console.print(
                    f"\n[bold green]✓ Successfully generated consolidated schema[/bold green]\n"
                    f"  Models: {total_models}\n"
                    f"  File: {all_results['__consolidated__']}"
                )
            else:
                # Create a nice table for non-verbose output
                table = Table(title=f"\n✓ Successfully generated {total_models} schema(s)")
                table.add_column("Model", style="cyan", no_wrap=True)
                table.add_column("Schema File", style="green")

                for model_name, schema_path in all_results.items():
                    table.add_row(model_name, str(schema_path))

                console.print(table)
        else:
            if config.single_file:
                console.print(
                    f"\n[bold green]✓ Complete![/bold green] "
                    f"Generated consolidated schema with {total_models} models"
                )
            else:
                console.print(
                    f"\n[bold green]✓ Complete![/bold green] Generated {total_models} schemas"
                )

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
