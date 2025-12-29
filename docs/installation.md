# Installation

KNL supports two installation modes: **repo-local** (isolated per repository) and **user-local** (system-wide).

## Requirements

- **Python 3.8+** for installer (uses only stdlib)
- **Python 3.14+** for KNL itself (uses modern Python features)
- **UV** (Python package manager - installer can install it for you)
- **Git repository** (optional, but recommended)

## Installation Modes

### Repo-Local Installation (Default)

When running the installer inside a git repository, KNL installs to `.knl/` in the current directory. This keeps KNL isolated per project.

```bash
cd your-repo
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh
```

**Benefits:**

- Each repository has its own isolated KNL installation
- No PATH pollution
- Easy to version-control KNL version per project
- Minimal impact on repository (only `.knl/` and `.knowledge/` folders)

**After installation:**

```bash
# Add to PATH for this session
export PATH="$(pwd)/.knl/bin:$PATH"

# Or add to your shell config for persistence
echo 'export PATH="$(pwd)/.knl/bin:$PATH"' >> ~/.bashrc
```

### User-Local Installation

For system-wide installation, use the `--user-local` flag or run outside a git repository:

```bash
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --user-local
```

This installs KNL to `~/.local/knl/` and automatically adds it to your PATH.

**Benefits:**

- Available globally across all projects
- Only need to install once
- Automatically added to PATH

## Version Management

Install specific versions or refs:

```bash
# Install specific version
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --version v0.1.0

# Install from branch or tag
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --ref develop

# Install from custom repo
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --repo yourname/knl
```

## What the Installer Does

The installer is smart and will:

1. **Find Python 3.8+** to run the installer itself (uses only stdlib)
2. **Find Python 3.14+** for KNL from PATH and common locations:
   - User installations (`~/.local`, `~/bin`)
   - pyenv installations (`~/.pyenv/versions/`)
   - Homebrew (macOS: `/opt/homebrew`, `/usr/local`)
   - Conda/Miniconda environments
   - System installations
3. **Detect git repository** and choose appropriate installation location
4. Install UV if needed
5. Create isolated virtual environment for KNL
6. Install KNL using the detected Python
7. Create wrapper scripts (`knl` and `kdt` alias)
8. Update `.gitignore` (repo-local only)
9. Create initial configuration in `~/.cache/knl/` (XDG-compliant)

!!! note "No sudo required"
    All installation happens in user directories. No root privileges needed.

## Manual Installation

```bash
# Clone the repository
git clone https://github.com/akaliazin/knl.git
cd knl

# Run the installer
./install.sh

# Or install with UV directly
uv pip install -e .
```

## Verifying Installation

```bash
# Check KNL version
knl --version

# Check installation location
which knl

# View help
knl --help
```

## Upgrading

To upgrade KNL to the latest version:

```bash
# For repo-local installation
cd your-repo
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh

# For user-local installation
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --user-local
```

## Uninstalling

### Repo-Local Installation

```bash
cd your-repo
rm -rf .knl
# Optionally remove knowledge base
rm -rf .knowledge
```

### User-Local Installation

```bash
rm -rf ~/.local/knl
# Remove from PATH in your shell config (~/.bashrc, ~/.zshrc)
```

### Global Configuration

```bash
# Remove global config (XDG-compliant)
rm -rf ~/.cache/knl
```

## Troubleshooting

### Python Not Found

If the installer can't find Python 3.14+, it will guide you through installation options:

- **pyenv** (recommended for Linux/macOS)
- **Homebrew** (macOS)
- **python.org** installer
- **Build from source**
- **Miniconda**

### UV Installation Fails

If UV installation fails:

```bash
# Install UV manually
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then run KNL installer again
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh
```

### Permission Denied

If you get permission errors:

- Make sure you're not using `sudo` - it's not needed
- Check that your user has write permissions to the installation directory
- For repo-local: Make sure you own the repository directory

## Next Steps

- [Quick Start Guide](quickstart.md) - Learn how to use KNL
- [Configuration](configuration.md) - Customize KNL settings
- [Task Management](guide/tasks.md) - Create and manage tasks
