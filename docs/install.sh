#!/usr/bin/env bash
# KNL (Knowledge Retention Library) installer
# Minimal bash wrapper around Python installer

set -e

# Find Python 3.8+
PYTHON_CMD=""

# Try to find a compatible Python
for cmd in python3 python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python; do
    if command -v "$cmd" &> /dev/null; then
        # Check if version is 3.8+
        version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0")
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)

        if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.8+ is required to run the installer."
    echo "Please install Python 3.8 or later and try again."
    echo ""
    echo "Installation options:"
    echo "  - pyenv: https://github.com/pyenv/pyenv"
    echo "  - python.org: https://www.python.org/downloads/"
    echo "  - Homebrew (macOS): brew install python3"
    exit 1
fi

# Run the embedded Python installer
"$PYTHON_CMD" - "$@" << 'PYTHON_INSTALLER'
#!/usr/bin/env python3
"""
KNL (Knowledge Retention Library) Installer
Pure Python implementation using only stdlib (Python 3.8+)
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional, Tuple


# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def print_banner():
    """Print KNL banner."""
    banner = r"""    __    __ _   __ __
   / /__ / /| | / // /
  / //_// / / |/ // /
 / ,<  / / /|   // /___
/_/|_|/_/ /_/|_//_____/

Knowledge Retention Library
"""
    print(banner)


def print_info(msg: str):
    """Print info message."""
    print(f"{Colors.BLUE}==>{Colors.NC} {msg}")


def print_success(msg: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {msg}")


def print_error(msg: str):
    """Print error message."""
    print(f"{Colors.RED}Error:{Colors.NC} {msg}", file=sys.stderr)


def print_warning(msg: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}Warning:{Colors.NC} {msg}")


def print_step(msg: str):
    """Print step message."""
    print(f"\n{Colors.CYAN}==>{Colors.NC} {Colors.BLUE}{msg}{Colors.NC}")


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    return (Path.cwd() / '.git').exists()


def get_install_location(force_user_local: bool = False) -> Path:
    """
    Determine installation location.

    Args:
        force_user_local: Force user-local installation

    Returns:
        Path to installation directory
    """
    if force_user_local:
        return Path.home() / '.local' / 'knl'

    if is_git_repo():
        return Path.cwd() / '.knl'

    return Path.home() / '.local' / 'knl'


def get_config_location() -> Path:
    """Get configuration directory location (XDG-compliant)."""
    xdg_cache = os.environ.get('XDG_CACHE_HOME')
    if xdg_cache:
        return Path(xdg_cache) / 'knl'
    return Path.home() / '.cache' / 'knl'


def check_python_version(min_version: str = "3.14") -> Tuple[bool, str]:
    """
    Check if current Python meets minimum version requirement.

    Args:
        min_version: Minimum required Python version (e.g., "3.14")

    Returns:
        Tuple of (is_compatible, current_version)
    """
    current = f"{sys.version_info.major}.{sys.version_info.minor}"

    # Parse versions
    min_major, min_minor = map(int, min_version.split('.'))
    cur_major, cur_minor = sys.version_info.major, sys.version_info.minor

    is_compatible = (cur_major > min_major or
                    (cur_major == min_major and cur_minor >= min_minor))

    return is_compatible, current


def find_python_for_knl(min_version: str = "3.14") -> Optional[str]:
    """
    Find a Python interpreter that meets KNL's requirements.

    Args:
        min_version: Minimum required Python version

    Returns:
        Path to compatible Python interpreter or None
    """
    # Extract minor version for search
    min_major, min_minor = map(int, min_version.split('.'))

    # Build list of Python commands to try
    python_cmds = []

    # Add versioned pythons from min_minor to 30
    for minor in range(min_minor, 31):
        python_cmds.append(f"python{min_major}.{minor}")

    # Add generic commands
    python_cmds.extend(['python3', 'python'])

    # Try each command
    for cmd in python_cmds:
        python_path = shutil.which(cmd)
        if not python_path:
            continue

        try:
            # Get version
            result = subprocess.run(
                [python_path, '-c',
                 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                continue

            version = result.stdout.strip()
            major, minor = map(int, version.split('.'))

            # Check if compatible
            if major > min_major or (major == min_major and minor >= min_minor):
                return python_path

        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            continue

    return None


def check_uv() -> bool:
    """Check if UV is installed."""
    return shutil.which('uv') is not None


def install_uv():
    """Install UV package manager."""
    print_step("Installing UV...")

    # Use curl or wget
    if shutil.which('curl'):
        cmd = ['curl', '-LsSf', 'https://astral.sh/uv/install.sh']
    elif shutil.which('wget'):
        cmd = ['wget', '-qO-', 'https://astral.sh/uv/install.sh']
    else:
        print_error("Neither curl nor wget found. Please install one of them.")
        sys.exit(1)

    # Run installer
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
        # Pipe to sh
        subprocess.run(['sh'], input=result.stdout, check=True)
        print_success("UV installed")

        # Add to PATH for this session
        cargo_bin = Path.home() / '.cargo' / 'bin'
        if cargo_bin.exists():
            os.environ['PATH'] = f"{cargo_bin}:{os.environ['PATH']}"

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install UV: {e}")
        sys.exit(1)


def get_latest_version(repo: str = "akaliazin/knl") -> Optional[str]:
    """
    Get the latest release version from GitHub.

    Args:
        repo: GitHub repository (owner/repo)

    Returns:
        Latest version tag or None
    """
    try:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            return data.get('tag_name')
    except Exception:
        return None


def download_and_install_knl(
    install_dir: Path,
    python_cmd: str,
    version: Optional[str] = None,
    ref: Optional[str] = None,
    repo: str = "akaliazin/knl"
):
    """
    Download and install KNL.

    Args:
        install_dir: Installation directory
        python_cmd: Python interpreter to use for KNL
        version: Specific version to install
        ref: Git ref to install from (branch/tag)
        repo: GitHub repository
    """
    print_step(f"Installing KNL with Python: {python_cmd}")

    # Create installation directory
    install_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a local development install
    is_local_dev = (Path.cwd() / '.git').exists() and (Path.cwd() / 'pyproject.toml').exists()

    if is_local_dev:
        print_info("Installing from local directory (development mode)...")
    else:
        print_info("Installing from GitHub...")

    # Create virtual environment
    venv_dir = install_dir / 'venv'
    print_info(f"Creating virtual environment in {venv_dir}...")

    try:
        subprocess.run(
            [python_cmd, '-m', 'venv', str(venv_dir)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        sys.exit(1)

    # Get venv python
    if platform.system() == 'Windows':
        venv_python = venv_dir / 'Scripts' / 'python.exe'
    else:
        venv_python = venv_dir / 'bin' / 'python'

    # Install KNL
    if is_local_dev:
        # Install in editable mode from local directory
        try:
            subprocess.run(
                ['uv', 'pip', 'install', '--python', str(venv_python), '-e', '.'],
                check=True,
                cwd=Path.cwd()
            )
            print_success("KNL installed in development mode")
            # Store version information
            version_file = install_dir / '.version'
            version_file.write_text(f"local-dev:{Path.cwd()}")
            return
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install KNL: {e}")
            sys.exit(1)

    # Remote installation - determine what to install
    if version:
        package_spec = f"git+https://github.com/{repo}.git@{version}"
    elif ref:
        package_spec = f"git+https://github.com/{repo}.git@{ref}"
    else:
        # Get latest version or use main branch
        latest = get_latest_version(repo)
        if latest:
            print_info(f"Latest version: {latest}")
            package_spec = f"git+https://github.com/{repo}.git@{latest}"
        else:
            print_warning("Could not fetch latest version, using main branch")
            package_spec = f"git+https://github.com/{repo}.git"

    # Install KNL using UV
    try:
        subprocess.run(
            ['uv', 'pip', 'install', '--python', str(venv_python), package_spec],
            check=True
        )
        print_success("KNL installed")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install KNL: {e}")
        sys.exit(1)

    # Store version information
    version_file = install_dir / '.version'
    version_file.write_text(package_spec)


def create_wrapper_script(install_dir: Path, is_repo_local: bool):
    """
    Create wrapper script for knl command.

    Args:
        install_dir: Installation directory
        is_repo_local: Whether this is a repo-local installation
    """
    print_step("Creating wrapper scripts...")

    # Determine venv location
    venv_dir = install_dir / 'venv'

    if platform.system() == 'Windows':
        knl_bin = venv_dir / 'Scripts' / 'knl.exe'
        bin_dir = install_dir / 'bin'
    else:
        knl_bin = venv_dir / 'bin' / 'knl'
        bin_dir = install_dir / 'bin'

    # Create bin directory
    bin_dir.mkdir(parents=True, exist_ok=True)

    # Create wrapper script
    wrapper = bin_dir / 'knl'

    if platform.system() == 'Windows':
        # Windows batch script
        wrapper_content = f"""@echo off
"{knl_bin}" %*
"""
        wrapper.write_text(wrapper_content)
    else:
        # Unix shell script
        wrapper_content = f"""#!/usr/bin/env bash
exec "{knl_bin}" "$@"
"""
        wrapper.write_text(wrapper_content)
        wrapper.chmod(0o755)

    # Create kdt alias
    kdt_wrapper = bin_dir / 'kdt'
    if platform.system() == 'Windows':
        kdt_content = f"""@echo off
"{knl_bin}" %*
"""
        kdt_wrapper.write_text(kdt_content)
    else:
        kdt_content = f"""#!/usr/bin/env bash
exec "{knl_bin}" "$@"
"""
        kdt_wrapper.write_text(kdt_content)
        kdt_wrapper.chmod(0o755)

    print_success(f"Created wrapper scripts in {bin_dir}")


def setup_path(install_dir: Path, is_repo_local: bool):
    """
    Add installation directory to PATH.

    Args:
        install_dir: Installation directory
        is_repo_local: Whether this is a repo-local installation
    """
    bin_dir = install_dir / 'bin'

    # Check if already in PATH
    path_env = os.environ.get('PATH', '')
    if str(bin_dir) in path_env:
        print_success(f"{bin_dir} already in PATH")
        return

    print_step(f"Adding {bin_dir} to PATH...")

    # Detect shell and config file
    shell = os.environ.get('SHELL', '')

    if 'bash' in shell:
        shell_config = Path.home() / '.bashrc'
    elif 'zsh' in shell:
        shell_config = Path.home() / '.zshrc'
    elif 'fish' in shell:
        shell_config = Path.home() / '.config' / 'fish' / 'config.fish'
    else:
        print_warning(f"Unknown shell: {shell}")
        print_info(f"Please manually add {bin_dir} to your PATH")
        return

    # Add to shell config
    marker = "# KNL (Knowledge Retention Library)"
    path_line = f'export PATH="{bin_dir}:$PATH"'

    if shell_config.exists():
        content = shell_config.read_text()
        if marker in content:
            print_success(f"PATH already configured in {shell_config}")
            return

    # Append to config
    with shell_config.open('a') as f:
        f.write(f"\n{marker}\n{path_line}\n")

    print_success(f"Added to PATH in {shell_config}")
    print_info(f"Please restart your shell or run: source {shell_config}")


def update_gitignore(install_dir: Path):
    """
    Update .gitignore to exclude KNL directories.

    Args:
        install_dir: Installation directory
    """
    # Only update if this is a repo-local install
    if not is_git_repo():
        return

    print_step("Updating .gitignore...")

    gitignore = Path.cwd() / '.gitignore'
    entries = ['.knl/', '.knowledge/']

    if gitignore.exists():
        content = gitignore.read_text()
        lines = content.splitlines()
    else:
        lines = []

    # Check what needs to be added
    to_add = []
    for entry in entries:
        if entry not in lines:
            to_add.append(entry)

    if not to_add:
        print_success(".gitignore already configured")
        return

    # Add entries
    with gitignore.open('a') as f:
        if lines and lines[-1]:  # Add blank line if file doesn't end with one
            f.write('\n')
        f.write('# KNL (Knowledge Retention Library)\n')
        for entry in to_add:
            f.write(f'{entry}\n')

    print_success("Updated .gitignore")


def create_initial_config(config_dir: Path):
    """
    Create initial configuration.

    Args:
        config_dir: Configuration directory
    """
    print_step("Creating initial configuration...")

    # Create config directory
    (config_dir / 'templates').mkdir(parents=True, exist_ok=True)
    (config_dir / 'cache').mkdir(parents=True, exist_ok=True)

    # Create default config
    config_file = config_dir / 'config.toml'
    if config_file.exists():
        print_success("Configuration already exists")
        return

    config_content = """# KNL Global Configuration
# This file is managed by KNL. Edit with: knl config edit

[task]
id_format = "jira"
jira_project = ""
github_repo = ""
auto_detect_from_branch = true

[integrations.jira]
enabled = false
url = ""
project = ""

[integrations.github]
enabled = false
repo = ""

[integrations.ai]
enabled = true
provider = "claude"
model = "claude-sonnet-4-5-20250929"

color_output = true
verbose = false
"""

    config_file.write_text(config_content)
    print_success("Created default configuration")


def main():
    """Main installer function."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Install KNL (Knowledge Retention Library)'
    )
    parser.add_argument(
        '--user-local',
        action='store_true',
        help='Install to user-local directory instead of repo-local'
    )
    parser.add_argument(
        '--version',
        help='Specific version to install (e.g., v0.1.0)'
    )
    parser.add_argument(
        '--ref',
        help='Git ref to install from (branch/tag)'
    )
    parser.add_argument(
        '--repo',
        default='akaliazin/knl',
        help='GitHub repository (default: akaliazin/knl)'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()
    print_info("Starting KNL installation...\n")

    # Determine installation location
    install_dir = get_install_location(args.user_local)
    is_repo_local = is_git_repo() and not args.user_local

    print_info(f"Installation location: {install_dir}")
    print_info(f"Installation type: {'repo-local' if is_repo_local else 'user-local'}\n")

    # Get config location
    config_dir = get_config_location()
    print_info(f"Configuration directory: {config_dir}\n")

    # Find Python for KNL
    print_step("Finding Python for KNL...")

    # Try to get minimum version from pyproject.toml if in repo
    min_version = "3.14"
    pyproject = Path.cwd() / 'pyproject.toml'
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'requires-python\s*=\s*["\']>=\s*(\d+\.\d+)', content)
            if match:
                min_version = match.group(1)
                print_info(f"Minimum Python version from pyproject.toml: {min_version}")
        except Exception:
            pass

    python_cmd = find_python_for_knl(min_version)

    if not python_cmd:
        print_error(f"Could not find Python {min_version}+ for KNL")
        print_info("\nPlease install Python {min_version}+ and try again.")
        print_info("Installation options:")
        print_info("  - pyenv: https://github.com/pyenv/pyenv")
        print_info("  - python.org: https://www.python.org/downloads/")
        print_info("  - Homebrew (macOS): brew install python@{min_version}")
        sys.exit(1)

    # Get Python version
    result = subprocess.run(
        [python_cmd, '-c',
         'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")'],
        capture_output=True,
        text=True
    )
    python_version = result.stdout.strip()
    print_success(f"Found Python {python_version} at {python_cmd}\n")

    # Check UV
    if not check_uv():
        print_warning("UV not found")
        response = input("UV is required. Install it now? (y/n) ").strip().lower()
        if response in ('y', 'yes'):
            install_uv()
        else:
            print_error("UV is required to install KNL. Aborting.")
            sys.exit(1)
    else:
        print_success("UV found\n")

    # Install KNL
    download_and_install_knl(
        install_dir,
        python_cmd,
        version=args.version,
        ref=args.ref,
        repo=args.repo
    )

    # Create wrapper scripts
    create_wrapper_script(install_dir, is_repo_local)

    # Setup PATH (only for user-local installations)
    if not is_repo_local:
        setup_path(install_dir, is_repo_local)
    else:
        print_info(f"\nFor repo-local installation, add to your PATH:")
        print_info(f"  export PATH=\"{install_dir / 'bin'}:$PATH\"")

    # Update .gitignore (only for repo-local installations)
    if is_repo_local:
        update_gitignore(install_dir)

    # Create initial configuration
    create_initial_config(config_dir)

    # Print success message
    print()
    print_success("KNL installed successfully!\n")
    print_info(f"Installation directory: {install_dir}")
    print_info(f"Python used: {python_cmd} ({python_version})")
    print_info(f"Configuration: {config_dir}\n")
    print_info("Next steps:")
    if not is_repo_local:
        print("  1. Restart your shell or source your shell config")
    else:
        print(f"  1. Add to PATH: export PATH=\"{install_dir / 'bin'}:$PATH\"")
    print("  2. Navigate to a repository")
    print("  3. Initialize KNL: knl init")
    print("  4. Create a task: knl create TASK-123")
    print("  5. Get help: knl --help\n")
    print_info(f"For more information, visit: https://github.com/{args.repo}")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Installation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

PYTHON_INSTALLER
