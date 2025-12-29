# Installation Architecture

*This page is under construction.*

KNL supports two installation modes to provide flexibility for different development workflows.

## Installation Modes

### Repo-Local Installation

The default installation mode that creates a KNL environment within your repository:

```
<repo>/.knl/
├── bin/
│   └── knl          # Wrapper script
├── venv/            # KNL's virtual environment
└── .python-version  # Pinned Python version for KNL
```

**Benefits:**
- Isolated per-repository
- Version controlled (optionally)
- Team-wide consistency
- No global installation conflicts

### User-Local Installation

Alternative installation mode that creates a single KNL environment in your home directory:

```
~/.local/knl/
├── bin/
│   └── knl          # Wrapper script
├── venv/            # KNL's virtual environment
└── .python-version  # Pinned Python version for KNL
```

**Benefits:**
- Single installation for all repositories
- Smaller disk footprint
- Simpler updates
- Works outside git repositories

## Installation Process

The installer performs the following steps:

1. **Python Discovery**: Finds Python 3.14+ automatically or uses specified version
2. **Virtual Environment**: Creates isolated venv for KNL
3. **Package Installation**: Installs KNL and dependencies using UV
4. **Wrapper Creation**: Creates executable wrapper scripts
5. **Version Pinning**: Records Python version in `.python-version`
6. **Configuration**: Sets up initial configuration

## Version Management

Install specific versions:

```bash
# Latest release
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh

# Specific version
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --version v1.0.0

# Development branch
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --ref develop
```

## Next Steps

- [Installation Guide](../installation.md) - Install KNL
- [Context Separation](context.md) - Understand context isolation
- [Principles](principles.md) - Architecture principles
