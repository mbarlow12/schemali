# Contributing to Schemali

Thank you for your interest in contributing to Schemali! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Issue Guidelines](#issue-guidelines)
- [CI/CD Workflows](#cicd-workflows)
- [Release Process](#release-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Getting Started

Before contributing, please:

1. Check existing [issues](https://github.com/mbarlow12/schemali/issues) to avoid duplicates
2. For major changes, open an issue first to discuss your proposal
3. Fork the repository and create a feature branch
4. Follow the development setup instructions below

## Development Setup

### Prerequisites

- Python >= 3.8
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Initial Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone your fork
git clone https://github.com/YOUR_USERNAME/schemali.git
cd schemali

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in development mode with dev dependencies
uv pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run tests to ensure everything is working
pytest

# Check linting
ruff check .

# Run the CLI
schemali --help
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clean, readable code following our [style guidelines](#code-style-guidelines)
- Add or update tests for your changes
- Update documentation as needed (README, docstrings, etc.)

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov-report=html
open htmlcov/index.html

# Run specific test file
pytest tests/test_schema_writer.py

# Run tests with verbose output
pytest -v
```

### 4. Lint and Format

```bash
# Check code with ruff
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .
```

### 5. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature (triggers minor release)
- `fix`: Bug fix (triggers patch release)
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `build`: Build system changes
- `ci`: CI configuration changes
- `chore`: Other changes (maintenance, etc.)

**Examples:**

```bash
git commit -m "feat: add support for custom schema validators"
git commit -m "fix: resolve issue with nested model processing"
git commit -m "docs: update installation instructions"
git commit -m "test: add tests for config file loading"
```

**Breaking Changes:**

For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in the footer:

```bash
git commit -m "feat!: redesign CLI interface"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

- **PEP 8**: Follow PEP 8 conventions (enforced by Ruff)
- **Line Length**: Maximum 100 characters
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings for modules, classes, and functions
- **Imports**: Sorted and organized (handled by Ruff)

### Example

```python
from typing import Optional

def process_schema(
    model_path: str,
    output_dir: Optional[str] = None,
    indent: int = 2
) -> dict[str, str]:
    """Process a Pydantic model and generate JSON schema.

    Args:
        model_path: Path to the Python module containing models.
        output_dir: Directory for output files. Defaults to current directory.
        indent: JSON indentation spaces (0-8).

    Returns:
        Dictionary mapping model names to output file paths.

    Raises:
        ValueError: If model_path is invalid.
        IOError: If output directory is not writable.
    """
    # Implementation
    pass
```

### Architecture Principles

- **Single Responsibility**: Each module/class should have one clear purpose
- **Type Safety**: Leverage Pydantic and type hints for validation
- **Testability**: Write testable code with minimal dependencies
- **Configuration**: Use pydantic-settings for all configuration

## Testing

### Test Coverage Goals

- Maintain **>85%** code coverage
- All public APIs must have tests
- Critical paths must have integration tests

### Test Organization

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── test_cli.py           # CLI interface tests
├── test_config.py        # Configuration tests
└── test_schema_writer.py # Core functionality tests
```

### Writing Tests

```python
def test_feature(sample_model_file, temp_dir):
    """Test description following Given-When-Then pattern."""
    # Arrange (Given)
    writer = SchemaWriter(output_dir=temp_dir)

    # Act (When)
    result = writer.process_module(sample_model_file)

    # Assert (Then)
    assert len(result) > 0
    assert all(path.exists() for path in result.values())
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=schemali --cov-report=term-missing

# Run specific test
pytest tests/test_cli.py::test_basic_usage -v

# Run with markers
pytest -m "not slow"
```

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally (`pytest`)
- [ ] Code is linted (`ruff check .`)
- [ ] Code is formatted (`ruff format .`)
- [ ] Coverage is maintained (>85%)
- [ ] Documentation is updated
- [ ] Commit messages follow conventional commits
- [ ] Branch is up to date with main

### PR Description Template

When creating a PR, include:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Changes Made
- List of key changes
- Another change

## Testing
How has this been tested?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Checklist
- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)
```

### Review Process

1. Automated checks will run (tests, linting, coverage)
2. At least one maintainer review is required
3. Address any feedback or requested changes
4. Once approved, a maintainer will merge your PR

## Issue Guidelines

### Reporting Bugs

When reporting bugs, please include:

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Ubuntu 22.04, macOS 13, Windows 11]
- Python version: [e.g., 3.11.4]
- Schemali version: [e.g., 0.1.0]
- Installation method: [e.g., pip, uv, from source]

## Additional Context
Any other relevant information, logs, or screenshots
```

### Feature Requests

For feature requests:

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How do you envision this working?

## Alternatives Considered
Other approaches you've considered

## Additional Context
Any mockups, examples, or references
```

## CI/CD Workflows

Our CI/CD pipeline uses GitHub Actions with several automated workflows:

### Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `claude/**` branches
- Pull requests to `main`

**Features:**
- Tests against Python 3.9, 3.10, 3.11, and 3.12
- Generates coverage reports
- Uploads coverage to Codecov (Python 3.11)
- Requires 85% minimum coverage

### Lint & Format Workflow (`lint-format.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main`

**Features:**
- Lints code with ruff
- Checks code formatting
- Auto-fixes issues on merge to main
- Creates automatic commits with fixes (tagged with `[skip ci]`)

### Release Workflow (`release.yml`)

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Features:**
- Runs full test suite
- Builds package with uv
- Uses semantic-release for versioning
- Publishes to PyPI
- Creates GitHub releases with artifacts

### Reusable Actions

Located in `.github/actions/`:

- **setup-uv**: Sets up Python environment with uv
- **build**: Builds the Python package
- **test**: Runs pytest with coverage
- **lint**: Runs ruff linter
- **format**: Formats code with ruff

### Testing Workflows Locally

Use [act](https://github.com/nektos/act) to test workflows locally:

```bash
# Install act
brew install act  # macOS
# or follow instructions at https://github.com/nektos/act

# Test the unit tests workflow
act -j test

# Test the lint workflow
act -j lint
```

## Release Process

Releases are automated using [semantic-release](https://github.com/semantic-release/semantic-release):

### How It Works

1. **Commit with Conventional Commits format** (see [commit guidelines](#5-commit-your-changes))
2. **Push to main** or merge PR to main
3. **Automated release workflow**:
   - Analyzes commits since last release
   - Determines version bump (major/minor/patch)
   - Generates CHANGELOG
   - Updates version in `pyproject.toml` and `schemali/cli.py`
   - Creates git tag and GitHub release
   - Publishes to PyPI

### Version Bumps

Based on commit types:

- `fix:` → Patch release (0.1.0 → 0.1.1)
- `feat:` → Minor release (0.1.0 → 0.2.0)
- `BREAKING CHANGE:` or `feat!:` → Major release (0.1.0 → 1.0.0)
- `docs:`, `refactor:`, `perf:` → Patch release
- `test:`, `ci:`, `chore:` → No release

### Manual Release (if needed)

```bash
# Update version in pyproject.toml and cli.py
# Run full test suite
pytest

# Build package
uv build

# Create and push tag
git tag v0.x.0
git push --tags
```

## Common Development Tasks

### Adding a New Dependency

```bash
# Add runtime dependency
uv pip install <package>
# Then add to pyproject.toml [project.dependencies]

# Add dev dependency
uv pip install <package>
# Then add to pyproject.toml [project.optional-dependencies.dev]
```

### Adding a New CLI Command

1. Add function in `schemali/cli.py` with `@app.command()` decorator
2. Use Typer's type hints for automatic validation
3. Add tests in `tests/test_cli.py`
4. Update README.md with usage examples

### Adding a New Configuration Option

1. Add field to `SchemaliConfig` in `schemali/config.py`
2. Add tests in `tests/test_config.py`
3. Update documentation in README.md

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
uv pip install -e ".[dev]"
```

### Coverage Issues

```bash
# Ensure pytest-cov is installed
uv pip install pytest-cov

# Run with explicit coverage
pytest --cov=schemali --cov-report=term-missing
```

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

## Questions?

If you have questions:

1. Check existing [issues](https://github.com/mbarlow12/schemali/issues)
2. Review [README.md](README.md) and [CLAUDE.md](CLAUDE.md)
3. Open a new issue with the `question` label

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.
