# Installation

KNL supports multiple installation modes and formats for maximum flexibility.

## Requirements

### Source Installation (Default)

- **Python 3.8+** for installer (uses only stdlib)
- **Python 3.14+** for KNL itself (uses modern Python features)
- **UV** (Python package manager - installer can install it for you)
- **Git repository** (optional, but recommended)

### Compiled Binary Installation (Portable)

- **Python 3.8+** to run the compiled binary
- **Git repository** (optional, but recommended)
- No UV or virtual environment needed

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

### Compiled Binary Installation

For maximum portability and minimal dependencies:

```bash
# Install latest compiled binary (requires only Python 3.8+)
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled

# Install specific version
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled --version v1.2.0

# Install from local binary (for offline/airgapped environments)
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled --binary-path /path/to/knl.pyz

# User-local compiled installation
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled --user-local
```

**Benefits:**

- **Portable** - Single ~52MB self-contained file
- **Minimal Requirements** - Only Python 3.8+ needed (vs 3.14+ for source)
- **No Dependencies** - No UV or virtual environment required
- **Fast Deployment** - Perfect for CI/CD and distribution
- **Offline Ready** - Use `--binary-path` for airgapped environments

## Version Management

Install specific versions or refs:

```bash
# Install specific version (source)
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --version v1.2.0

# Install from branch or tag
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --ref develop

# Install from custom repo
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --repo yourname/knl

# Combine options (compiled + version + user-local)
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled --version v1.2.0 --user-local
```

## What the Installer Does

The installer is smart and adapts based on installation mode:

### Source Installation (Default)

1. **Find Python 3.8+** to run the installer itself (uses only stdlib)
2. **Find Python 3.14+** for KNL from PATH and common locations:
   - User installations (`~/.local`, `~/bin`)
   - pyenv installations (`~/.pyenv/versions/`)
   - Homebrew (macOS: `/opt/homebrew`, `/usr/local`)
   - Conda/Miniconda environments
   - System installations
3. **Detect git repository** and choose appropriate installation location
4. Install UV if needed (prompts if not found)
5. Create isolated virtual environment for KNL
6. Install KNL and dependencies using the detected Python
7. Create wrapper scripts (`knl` and `kdt` alias)
8. **Deploy knowledge crumbs** - curated development knowledge
9. Update `.gitignore` (repo-local only)
10. Create initial configuration in `~/.cache/knl/` (XDG-compliant)

### Compiled Binary Installation (`--compiled`)

1. **Find Python 3.8+** to run the binary (less restrictive than source)
2. **Download or copy binary**:
   - Downloads from GitHub releases (if `--version` specified)
   - Copies from local path (if `--binary-path` specified)
   - Uses latest release (if neither specified)
3. Install binary to appropriate location
4. Create wrapper scripts (`knl` and `kdt` alias)
5. **Deploy knowledge crumbs** - curated development knowledge
6. Update `.gitignore` (repo-local only)
7. Create initial configuration

### Knowledge Crumbs Deployment

Both installation modes deploy **knowledge crumbs** - curated, reusable development knowledge:

- Organized by category: DevOps, Testing, Security, Development
- LLM-friendly format with YAML frontmatter
- Self-contained, actionable guides
- Located in `<install-dir>/know-how/crumbs/`

Example crumbs:
- `devops/github-pages-setup.md` - GitHub Pages deployment guide
- More crumbs added with each release

!!! note "No sudo required"
    All installation happens in user directories. No root privileges needed.

## Manual Installation

```bash
# Clone the repository
git clone https://github.com/akaliazin/knl.git
cd knl

# Option 1: Run the installer (recommended)
./install.sh

# Option 2: Install with UV directly
uv pip install -e .

# Option 3: Build and install compiled binary
make build-binary
./install.sh --compiled --binary-path ./dist/knl.pyz
```

### Building Compiled Binary

To create your own compiled binary:

```bash
# Install shiv if not already installed
uv pip install shiv

# Build binary (creates dist/knl.pyz)
make build-binary

# Test the binary
./dist/knl.pyz --version

# Install from local binary
./install.sh --compiled --binary-path ./dist/knl.pyz
```

## Verifying Installation

```bash
# Check KNL version
knl --version

# Check installation location
which knl

# View help
knl --help

# Browse available knowledge crumbs
ls ~/.local/knl/know-how/crumbs/     # for user-local
ls .knl/know-how/crumbs/              # for repo-local

# Read a crumb
cat ~/.local/knl/know-how/crumbs/devops/github-pages-setup.md
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
