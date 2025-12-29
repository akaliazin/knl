# Development Setup

*This page is under construction.*

Guide for setting up a KNL development environment.

## Prerequisites

- Python 3.14 or higher
- Git
- UV (Python package manager) - optional but recommended

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/akaliazin/knl.git
cd knl

# Set up development environment
make dev

# Verify installation
uv run knl --version
```

## Manual Setup

### 1. Clone Repository

```bash
git clone https://github.com/akaliazin/knl.git
cd knl
```

### 2. Create Virtual Environment

```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Using standard venv
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install KNL in development mode with all dependencies
uv pip install -e ".[dev,docs]"

# Or using pip
pip install -e ".[dev,docs]"
```

### 4. Verify Installation

```bash
# Check KNL version
knl --version

# Run tests
pytest tests/ -v

# Check code quality
make check-all
```

## Development Workflow

### Running KNL Locally

```bash
# Run from source
uv run knl --help

# Or if virtual environment is activated
knl --help
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_config.py -v

# Run specific test
pytest tests/test_config.py::TestConfigManager::test_load_global_config -v
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make check-all
```

### Documentation

```bash
# Build documentation
make docs

# Serve documentation locally
make docs-serve
# Opens at http://127.0.0.1:8000/knl/

# Deploy documentation
make docs-deploy
```

## Project Structure

```
knl/
├── .venv/                # Virtual environment (created)
├── src/knl/              # Source code
│   ├── __init__.py       # Package version
│   ├── cli.py            # Main CLI entry point
│   ├── models/           # Pydantic models
│   │   ├── config.py     # Configuration models
│   │   └── task.py       # Task models
│   ├── core/             # Core business logic
│   │   ├── config.py     # Configuration manager
│   │   └── paths.py      # Path utilities
│   ├── commands/         # CLI commands
│   │   ├── init.py       # Repository initialization
│   │   ├── task.py       # Task management
│   │   └── config.py     # Configuration management
│   └── utils/            # Utilities
│       ├── patterns.py   # Pattern matching
│       └── git.py        # Git integration
├── tests/                # Test suite
│   ├── conftest.py       # Pytest configuration
│   ├── test_config.py    # Configuration tests
│   ├── test_task.py      # Task tests
│   └── ...
├── docs/                 # Documentation
│   ├── index.md          # Home page
│   ├── installation.md   # Installation guide
│   ├── guide/            # User guides
│   ├── architecture/     # Architecture docs
│   ├── cli/              # CLI reference
│   └── development/      # Development docs
├── install.sh            # Installer script
├── mkdocs.yml            # MkDocs configuration
├── pyproject.toml        # Project metadata
├── Makefile              # Development tasks
└── README.md             # Project readme
```

## Common Tasks

### Adding a New Command

1. Create command module in `src/knl/commands/`
2. Register in `src/knl/cli.py`
3. Add tests in `tests/`
4. Update documentation

### Adding a New Configuration Option

1. Update models in `src/knl/models/config.py`
2. Update `ConfigManager` in `src/knl/core/config.py`
3. Add tests
4. Update configuration documentation

### Adding Dependencies

```bash
# Add runtime dependency
# Edit pyproject.toml [project.dependencies]

# Add development dependency
# Edit pyproject.toml [project.optional-dependencies.dev]

# Add documentation dependency
# Edit pyproject.toml [project.optional-dependencies.docs]

# Reinstall
uv pip install -e ".[dev,docs]"
```

## Troubleshooting

### UV Not Installed

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Python Version Issues

```bash
# Check Python version
python --version

# KNL requires Python 3.14+
# Install via pyenv:
pyenv install 3.14.2
pyenv local 3.14.2
```

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,docs]"
```

### Test Failures

```bash
# Run tests with verbose output
pytest tests/ -vv

# Run specific test
pytest tests/test_config.py -vv

# Clear pytest cache
rm -rf .pytest_cache
```

## Next Steps

- [Contributing Guide](contributing.md) - Contribution guidelines
- [Testing Guide](testing.md) - Testing guidelines
- [Architecture Principles](../architecture/principles.md) - Understand the design
