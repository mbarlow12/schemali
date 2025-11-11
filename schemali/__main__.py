"""Allow running schemali as a module: python -m schemali"""

from .cli import app

if __name__ == "__main__":
    app()
