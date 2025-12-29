# Context Separation

*This page is under construction.*

KNL maintains strict separation between its own execution context and the target repository's context.

## Context Isolation

### KNL Context

The environment where KNL itself runs:

```
KNL_CONTEXT_DIR: <repo>/.knl/venv/  (or ~/.local/knl/venv/)
```

**Contains:**
- KNL's Python interpreter
- KNL's dependencies (typer, rich, pydantic, etc.)
- KNL's virtual environment
- KNL's Python version (.python-version)

### Target Context

The environment of the repository being worked on:

```
TARGET_CONTEXT_DIR: <repo>/
```

**Contains:**
- Project's source code
- Project's dependencies
- Project's virtual environment (if any)
- Project's Python version (if Python project)
- Project's build tools and configuration

## Why Context Separation Matters

### No Environment Bleeding

KNL's dependencies never interfere with your project:

- KNL uses Python 3.14+ with modern features
- Your project can use Python 3.8, 3.9, or any other version
- No PYTHONPATH conflicts
- No package version conflicts
- No virtual environment activation needed

### Cross-Language Support

KNL can manage tasks for projects in any language:

- Python projects
- Java/Groovy projects (Gradle, Maven)
- Node.js projects (npm, yarn)
- Go projects
- Rust projects
- Ruby projects
- Mixed-language projects

### Independent Updates

Update KNL without affecting your project:

```bash
# Update KNL itself
./install.sh

# Your project dependencies remain unchanged
# Your project Python version remains unchanged
```

## Implementation Details

### Environment Variables

KNL manages environment variables carefully:

- Clears Python-related variables when executing project commands
- Sets up clean environment for project tools
- Restores KNL environment after project operations

### Path Management

KNL maintains separate paths:

- KNL's `bin/` directory for KNL executable
- Project's `bin/` directory for project tools
- No path pollution between contexts

### Virtual Environment Handling

KNL detects and respects project virtual environments:

- Automatically detects `.venv/`, `venv/`, `virtualenv/`
- Uses project's venv for project operations
- Never mixes KNL's venv with project's venv

## Next Steps

- [Installation Architecture](installation.md) - Installation modes
- [Principles](principles.md) - Architecture principles
- [Configuration](../configuration.md) - Configure KNL
