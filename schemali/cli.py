"""Command-line interface for schemali."""

import argparse
import sys
from pathlib import Path

from .schema_writer import SchemaWriter


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='schemali',
        description='Generate JSON schemas from Pydantic models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single module
  schemali models.py

  # Process multiple modules
  schemali models.py user.py product.py

  # Specify output directory
  schemali models.py -o schemas/

  # Custom indentation
  schemali models.py --indent 4

  # Verbose output
  schemali models.py -v
        """
    )

    parser.add_argument(
        'modules',
        nargs='+',
        type=Path,
        help='Python module file(s) containing Pydantic models'
    )

    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=None,
        help='Output directory for schema files (default: current directory)'
    )

    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSON indentation spaces (default: 2)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )

    args = parser.parse_args()

    # Initialize schema writer
    writer = SchemaWriter(output_dir=args.output_dir)

    # Track results
    total_models = 0
    all_results = {}

    try:
        # Process each module
        for module_path in args.modules:
            module_path = module_path.resolve()

            if not module_path.exists():
                print(f"Error: Module file not found: {module_path}", file=sys.stderr)
                sys.exit(1)

            if not module_path.suffix == '.py':
                print(f"Warning: {module_path} is not a Python file, skipping", file=sys.stderr)
                continue

            # Process the module
            results = writer.process_module(
                module_path,
                indent=args.indent,
                verbose=args.verbose
            )

            total_models += len(results)
            all_results.update(results)

        # Summary
        if not args.verbose:
            print(f"Successfully generated {total_models} schema(s):")
            for model_name, schema_path in all_results.items():
                print(f"  {model_name} -> {schema_path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
