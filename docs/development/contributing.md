# Contributing to KNL

*This page is under construction.*

Thank you for your interest in contributing to KNL! This guide will help you get started.

## Quick Start

1. Fork the repository on GitHub
2. Clone your fork: `git clone https://github.com/your-username/knl.git`
3. Set up development environment: `make dev`
4. Create a feature branch: `git checkout -b feature/my-feature`
5. Make your changes
6. Run tests: `make test`
7. Submit a pull request

## Development Setup

See [Development Setup](setup.md) for detailed instructions on setting up your development environment.

## Code Style

KNL follows these conventions:

### Python Style

- Follow PEP 8
- Use Ruff for linting and formatting
- Type hints required (mypy strict mode)
- Line length: 100 characters
- Use `|` for union types, not `Optional` or `Union`

### Running Code Quality Checks

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

## Testing

See [Testing Guide](testing.md) for detailed testing guidelines.

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
pytest tests/test_config.py -v
```

### Writing Tests

- Place tests in `tests/` directory
- Follow pattern: `test_<module>.py` with `Test<Feature>` classes
- Aim for >80% coverage
- Use descriptive test names

## Commit Messages

Use clear, descriptive commit messages:

```
Add feature: Brief description

Longer explanation of what changed and why.

- Bullet points for specific changes
- Reference issues: Fixes #123
```

## Pull Request Process

1. **Create PR**: Open a pull request with a clear title and description
2. **Tests**: Ensure all tests pass
3. **Code Review**: Address review feedback
4. **Documentation**: Update documentation if needed
5. **Merge**: Maintainers will merge when ready

### PR Checklist

- [ ] Tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Code is linted (`make lint`)
- [ ] Type checks pass (`make type-check`)
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (if needed)

## Documentation

### Building Documentation

```bash
# Build documentation
make docs

# Serve documentation locally
make docs-serve

# Deploy to GitHub Pages
make docs-deploy
```

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add links to related topics
- Mark incomplete pages with "*This page is under construction.*"

## Project Structure

```
knl/
├── src/knl/              # Source code
│   ├── cli.py            # Main CLI entry point
│   ├── models/           # Pydantic models
│   ├── core/             # Core business logic
│   ├── commands/         # CLI command implementations
│   └── utils/            # Utility modules
├── tests/                # Test suite
├── docs/                 # Documentation
├── install.sh            # Installer script
└── pyproject.toml        # Project metadata
```

## Getting Help

- **Documentation**: https://akaliazin.github.io/knl/
- **Issues**: https://github.com/akaliazin/knl/issues
- **Discussions**: https://github.com/akaliazin/knl/discussions

## Code of Conduct

Be respectful and constructive in all interactions.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Next Steps

- [Development Setup](setup.md) - Set up your environment
- [Testing Guide](testing.md) - Write tests
- [Architecture Principles](../architecture/principles.md) - Understand the design
