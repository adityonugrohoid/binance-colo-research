# Project Template

[![CI](https://github.com/adityonugrohoid/template/actions/workflows/ci.yml/badge.svg)](https://github.com/adityonugrohoid/template/actions/workflows/ci.yml)

A Python project template implementing best practices for packaging, testing, and code quality, powered by [uv](https://github.com/astral-sh/uv).

## Features

- **Package Management**: `uv` for blazing fast dependency management.
- **Linting & Formatting**: [Ruff](https://docs.astral.sh/ruff/) for fast and comprehensive code quality checks.
- **Testing**: [Pytest](https://docs.pytest.org/) with coverage reporting.
- **Type Checking**: [MyPy](https://mypy.readthedocs.io/) for static type analysis.
- **CI/CD**: GitHub Actions workflow for automated testing and linting.
- **Pre-commit**: Git hooks to ensure code quality before committing.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/adityonugrohoid/template.git
    cd template
    ```

2.  **Install `uv` (if not already installed):**
    ```bash
    # On Windows
    pip install uv
    # Or see https://github.com/astral-sh/uv for other methods
    ```

3.  **Sync dependencies:**
    ```bash
    uv sync
    ```
    This command will create the virtual environment (`.venv`) and install all dependencies.

4.  **Install pre-commit hooks:**
    ```bash
    uv run pre-commit install
    ```

## Usage

### Running Tests

```bash
uv run pytest
```

### Linting and Formatting

```bash
uv run ruff check .
uv run ruff format .
```

### Type Checking

```bash
uv run mypy .
```

## Project Structure

```
.
├── .github/            # GitHub Actions workflows
├── src/                # Source code
│   └── template_package/
├── tests/              # Test suite
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```
