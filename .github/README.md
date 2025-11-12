# GitHub Actions CI/CD

This directory contains GitHub Actions workflows and reusable actions for the schemali project.

## Reusable Actions

Located in `.github/actions/`, these composite actions encapsulate common CI tasks:

### setup-uv
Sets up the Python environment using uv for fast, reliable dependency management.

**Inputs:**
- `python-version`: Python version to use (default: `3.11`)
- `install-dev`: Install dev dependencies (default: `true`)
- `cache-key`: Custom cache key suffix (default: `default`)

### build
Builds the Python package using uv.

**Inputs:**
- `output-dir`: Output directory for build artifacts (default: `dist`)

**Outputs:**
- `artifact-path`: Path to build artifacts

### test
Runs pytest with optional coverage reporting.

**Inputs:**
- `coverage`: Generate coverage report (default: `true`)
- `coverage-threshold`: Minimum coverage percentage required (default: `90`)
- `pytest-args`: Additional pytest arguments (default: `''`)

**Outputs:**
- `coverage-percentage`: Test coverage percentage

### lint
Runs ruff linter with optional auto-fix.

**Inputs:**
- `auto-fix`: Automatically fix linting issues (default: `false`)
- `paths`: Paths to lint (default: `schemali tests`)
- `fail-on-error`: Fail the action if linting errors are found (default: `true`)

### format
Formats code using ruff formatter.

**Inputs:**
- `paths`: Paths to format (default: `schemali tests`)
- `check-only`: Only check formatting without making changes (default: `false`)

## Workflows

### test.yml
Runs unit tests on push to main and claude/** branches, and on pull requests.

**Features:**
- Tests against Python 3.9, 3.10, 3.11, and 3.12
- Generates coverage reports
- Uploads coverage to Codecov (for Python 3.11)
- Requires 90% minimum coverage

**Triggers:**
- Push to `main` or `claude/**` branches
- Pull requests to `main`

### lint-format.yml
Runs linting and formatting checks, with automatic fixes on merge to main.

**Features:**
- Lints code with ruff
- Checks code formatting
- Auto-fixes issues on merge to main branch
- Creates automatic commits with fixes (with `[skip ci]` tag)

**Triggers:**
- Push to `main` branch
- Pull requests to `main`

### release.yml
Automated release workflow using semantic-release.

**Features:**
- Runs tests before release
- Builds package
- Uses semantic-release to determine version and generate changelog
- Publishes to PyPI (requires `PYPI_API_TOKEN` secret)
- Creates GitHub releases with build artifacts

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Secrets Required:**
- `PYPI_API_TOKEN`: PyPI API token for publishing packages

## Semantic Release

The project uses [semantic-release](https://github.com/semantic-release/semantic-release) with conventional commits.

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types and their effects:**
- `feat`: New feature (triggers minor release)
- `fix`: Bug fix (triggers patch release)
- `perf`: Performance improvement (triggers patch release)
- `docs`: Documentation changes (triggers patch release)
- `refactor`: Code refactoring (triggers patch release)
- `test`: Test changes (no release)
- `build`: Build system changes (no release)
- `ci`: CI configuration changes (no release)
- `chore`: Other changes (no release)

**Breaking Changes:**
- Add `BREAKING CHANGE:` in the commit footer or `!` after type to trigger major release
- Example: `feat!: redesign CLI interface`

### Release Process

1. Commit changes using conventional commit format
2. Push to main branch or merge PR
3. Release workflow runs automatically:
   - Analyzes commits since last release
   - Determines new version number
   - Generates CHANGELOG
   - Updates version in `pyproject.toml` and `schemali/cli.py`
   - Creates git tag and GitHub release
   - Publishes to PyPI

## Configuration Files

- `.releaserc.json`: Semantic-release configuration
- Individual workflow files in `.github/workflows/`
- Individual action files in `.github/actions/*/action.yml`

## Testing Workflows Locally

You can test workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act

# Test the unit tests workflow
act -j test

# Test the lint workflow
act -j lint
```

## Maintenance

When updating workflows or actions:

1. Test changes in a feature branch first
2. Ensure all required secrets are configured
3. Update this README if adding new workflows or actions
4. Use semantic-release commit messages for proper versioning
