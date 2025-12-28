#!/usr/bin/env bash
# KNL (Knowledge Retention Library) installer
# Robust Python detection and userland installation support

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/yourusername/knl"  # Update with actual repo
INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/knl"

# Python version will be extracted from pyproject.toml
MIN_PYTHON_VERSION=""

# Global variable for selected Python
PYTHON_CMD=""

# Functions
print_info() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

print_step() {
    echo -e "\n${CYAN}==>${NC} ${BLUE}$1${NC}"
}

extract_python_version() {
    # Extract minimum Python version from pyproject.toml
    # Looks for: requires-python = ">=X.Y" or requires-python = ">=X.Y.Z"

    local pyproject_file="pyproject.toml"

    # Check if we're in the repo directory
    if [ ! -f "$pyproject_file" ]; then
        # Fallback to default if pyproject.toml not found
        print_warning "pyproject.toml not found, using default Python version 3.14"
        MIN_PYTHON_VERSION="3.14"
        return
    fi

    # Extract the version using grep and sed
    local version_line
    version_line=$(grep "requires-python" "$pyproject_file" 2>/dev/null || echo "")

    if [ -z "$version_line" ]; then
        print_warning "requires-python not found in pyproject.toml, using default 3.14"
        MIN_PYTHON_VERSION="3.14"
        return
    fi

    # Extract version number (handles both >=3.14 and >=3.14.0)
    # Examples: ">=3.14", ">=3.14.0", ">= 3.14", ">=  3.14"
    MIN_PYTHON_VERSION=$(echo "$version_line" | sed -E 's/.*>=[[:space:]]*([0-9]+\.[0-9]+).*/\1/')

    if [ -z "$MIN_PYTHON_VERSION" ] || [ "$MIN_PYTHON_VERSION" = "$version_line" ]; then
        print_warning "Could not parse Python version from pyproject.toml, using default 3.14"
        MIN_PYTHON_VERSION="3.14"
        return
    fi

    print_info "Minimum Python version from pyproject.toml: ${MIN_PYTHON_VERSION}"
}

version_ge() {
    # Compare versions: returns 0 if $1 >= $2
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

get_python_version() {
    local python_cmd="$1"
    if [ -x "$python_cmd" ]; then
        "$python_cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0"
    else
        echo "0.0"
    fi
}

check_python_version_compatible() {
    local python_cmd="$1"
    local version=$(get_python_version "$python_cmd")

    if [ "$version" = "0.0" ]; then
        return 1
    fi

    version_ge "$version" "$MIN_PYTHON_VERSION"
}

search_python_in_path() {
    print_step "Searching for Python ${MIN_PYTHON_VERSION}+ in PATH..."

    # Extract minor version from MIN_PYTHON_VERSION (e.g., "14" from "3.14")
    local min_minor
    min_minor=$(echo "$MIN_PYTHON_VERSION" | cut -d. -f2)

    # Build list of Python commands to try
    # Start from the minimum version up to a reasonable future version (3.25)
    local python_cmds=()

    # Add versioned pythons from MIN_VERSION to 3.25
    for minor in $(seq "$min_minor" 25); do
        python_cmds+=("python3.$minor")
    done

    # Add generic python3 and python
    python_cmds+=("python3" "python")

    # Try each Python command
    for cmd in "${python_cmds[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            local full_path
            full_path=$(command -v "$cmd")
            local version
            version=$(get_python_version "$full_path")

            if [ "$version" != "0.0" ]; then
                echo "  Found: $full_path (Python $version)"

                if check_python_version_compatible "$full_path"; then
                    print_success "Compatible Python found: $full_path (Python $version)"
                    PYTHON_CMD="$full_path"
                    return 0
                fi
            fi
        fi
    done

    return 1
}

search_python_common_locations() {
    print_step "Searching common Python installation locations..."

    # Common directories to search for Python installations
    local search_dirs=(
        # User-local installations
        "$HOME/.local/bin"
        "$HOME/bin"

        # Homebrew (macOS)
        "/opt/homebrew/bin"
        "/opt/homebrew/opt/python@"*/bin
        "/usr/local/bin"
        "/usr/local/opt/python@"*/bin

        # System installations
        "/usr/bin"

        # pyenv installations
        "$HOME/.pyenv/versions/"*/bin

        # Conda/Miniconda
        "$HOME/miniconda3/bin"
        "$HOME/anaconda3/bin"
        "$HOME/.conda/envs/"*/bin
    )

    # Search each directory for python3* executables
    for dir_pattern in "${search_dirs[@]}"; do
        # Expand glob patterns
        for search_dir in $dir_pattern; do
            if [ ! -d "$search_dir" ]; then
                continue
            fi

            # Find all python3* executables in this directory
            # Look for: python3, python3.X, python3.XX
            for python_path in "$search_dir"/python3 "$search_dir"/python3.[0-9] "$search_dir"/python3.[0-9][0-9]; do
                if [ -x "$python_path" ]; then
                    local version
                    version=$(get_python_version "$python_path")

                    if [ "$version" != "0.0" ]; then
                        echo "  Found: $python_path (Python $version)"

                        if check_python_version_compatible "$python_path"; then
                            print_success "Compatible Python found: $python_path (Python $version)"
                            PYTHON_CMD="$python_path"
                            return 0
                        fi
                    fi
                fi
            done
        done
    done

    return 1
}

prompt_python_path() {
    print_step "Python ${MIN_PYTHON_VERSION}+ not found automatically"
    echo ""
    echo "Please choose an option:"
    echo "  1) Provide path to Python ${MIN_PYTHON_VERSION}+ interpreter"
    echo "  2) View installation instructions"
    echo "  3) Exit"
    echo ""

    while true; do
        read -p "Choice [1-3]: " choice

        case $choice in
            1)
                read -p "Enter full path to Python interpreter: " python_path

                if [ ! -x "$python_path" ]; then
                    print_error "File not found or not executable: $python_path"
                    continue
                fi

                local version=$(get_python_version "$python_path")

                if [ "$version" = "0.0" ]; then
                    print_error "Not a valid Python interpreter: $python_path"
                    continue
                fi

                if ! check_python_version_compatible "$python_path"; then
                    print_error "Python version $version is too old (need ${MIN_PYTHON_VERSION}+)"
                    continue
                fi

                print_success "Using Python $version from $python_path"
                PYTHON_CMD="$python_path"
                return 0
                ;;
            2)
                show_installation_instructions
                ;;
            3)
                print_info "Installation cancelled."
                exit 0
                ;;
            *)
                echo "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
}

show_installation_instructions() {
    # Extract version for display (e.g., "3.14")
    local version="$MIN_PYTHON_VERSION"
    local version_example="${version}.2"  # e.g., "3.14.2"

    cat << EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Python ${version}+ Installation Options (No sudo required)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1: pyenv (Recommended for Linux/macOS)
────────────────────────────────────────────────────────────────────
pyenv allows you to install and manage multiple Python versions in
your home directory without system permissions.

Installation:
  curl https://pyenv.run | bash

Then add to your shell config (~/.bashrc or ~/.zshrc):
  export PYENV_ROOT="\$HOME/.pyenv"
  export PATH="\$PYENV_ROOT/bin:\$PATH"
  eval "\$(pyenv init -)"

Restart your shell, then install Python ${version}:
  pyenv install ${version_example}
  pyenv global ${version_example}

Verify:
  python3 --version

More info: https://github.com/pyenv/pyenv


Option 2: Homebrew (macOS only)
────────────────────────────────────────────────────────────────────
If you have Homebrew installed:
  brew install python@${version}

More info: https://brew.sh/


Option 3: Standalone Python Build (Linux/macOS)
────────────────────────────────────────────────────────────────────
Build Python from source into ~/.local:

  wget https://www.python.org/ftp/python/${version_example}/Python-${version_example}.tgz
  tar -xzf Python-${version_example}.tgz
  cd Python-${version_example}
  ./configure --prefix=\$HOME/.local --enable-optimizations
  make -j\$(nproc)
  make install

Add to PATH in ~/.bashrc or ~/.zshrc:
  export PATH="\$HOME/.local/bin:\$PATH"

Verify:
  ~/.local/bin/python${version} --version


Option 4: python.org Installer (macOS/Windows)
────────────────────────────────────────────────────────────────────
Download from: https://www.python.org/downloads/
Choose "Download Python ${version}.x" and follow the installer.

For macOS: The installer places Python in:
  /Library/Frameworks/Python.framework/Versions/${version}/bin/python3


Option 5: Miniconda (All platforms)
────────────────────────────────────────────────────────────────────
Lightweight Python distribution manager:

  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash Miniconda3-latest-Linux-x86_64.sh

Create environment with Python ${version}:
  conda create -n py${version//./} python=${version}
  conda activate py${version//./}

More info: https://docs.conda.io/en/latest/miniconda.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After installing Python, run this installer again.

EOF
}

find_python() {
    print_step "Looking for Python ${MIN_PYTHON_VERSION}+..."

    # Try PATH first (fastest)
    if search_python_in_path; then
        return 0
    fi

    # Search common locations
    if search_python_common_locations; then
        return 0
    fi

    # Nothing found - prompt user
    prompt_python_path
}

check_uv() {
    if command -v uv &> /dev/null; then
        print_success "UV found: $(uv --version)"
        return 0
    else
        print_warning "UV not found"
        return 1
    fi
}

install_uv() {
    print_step "Installing UV..."

    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget &> /dev/null; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        print_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi

    # Source the shell config to make uv available
    if [ -f "${HOME}/.cargo/env" ]; then
        source "${HOME}/.cargo/env"
    fi

    print_success "UV installed"
}

install_knl() {
    print_step "Installing KNL with Python: $PYTHON_CMD"

    # Create installation directory
    mkdir -p "${INSTALL_DIR}"
    mkdir -p "${CONFIG_DIR}"

    # Use the selected Python with UV
    export UV_PYTHON="$PYTHON_CMD"

    # Determine installation method
    if [ -d ".git" ] && [ -f "pyproject.toml" ]; then
        # Local development installation
        print_info "Installing from local directory..."
        uv pip install --python "$PYTHON_CMD" --system -e .
    else
        # Remote installation
        print_info "Installing from GitHub..."
        uv pip install --python "$PYTHON_CMD" --system "git+${REPO_URL}.git"
    fi

    print_success "KNL installed"
}

setup_path() {
    # Check if install dir is in PATH
    if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
        print_step "Adding ${INSTALL_DIR} to PATH..."

        # Detect shell
        local shell_config=""
        case "$SHELL" in
            */bash)
                shell_config="${HOME}/.bashrc"
                ;;
            */zsh)
                shell_config="${HOME}/.zshrc"
                ;;
            */fish)
                shell_config="${HOME}/.config/fish/config.fish"
                ;;
            *)
                print_warning "Unknown shell: $SHELL. Please manually add ${INSTALL_DIR} to your PATH"
                return
                ;;
        esac

        # Add to shell config
        if [ -n "$shell_config" ]; then
            if [ -f "$shell_config" ]; then
                # Only add if not already present
                if ! grep -q "# KNL (Knowledge Retention Library)" "$shell_config"; then
                    echo "" >> "$shell_config"
                    echo "# KNL (Knowledge Retention Library)" >> "$shell_config"
                    echo "export PATH=\"${INSTALL_DIR}:\$PATH\"" >> "$shell_config"
                fi
            else
                echo "# KNL (Knowledge Retention Library)" > "$shell_config"
                echo "export PATH=\"${INSTALL_DIR}:\$PATH\"" >> "$shell_config"
            fi

            print_success "Added to PATH in $shell_config"
            print_info "Please restart your shell or run: source $shell_config"
        fi
    else
        print_success "${INSTALL_DIR} already in PATH"
    fi
}

create_initial_config() {
    print_step "Creating initial configuration..."

    # Initialize global config directory
    mkdir -p "${CONFIG_DIR}/templates"
    mkdir -p "${CONFIG_DIR}/cache"

    # Create default config if it doesn't exist
    local config_file="${CONFIG_DIR}/config.toml"
    if [ ! -f "$config_file" ]; then
        cat > "$config_file" << 'EOF'
# KNL Global Configuration
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
EOF
        print_success "Created default configuration"
    fi
}

print_banner() {
    cat << 'EOF'
    __    __ _   __ __
   / /__ / /| | / // /
  / //_// / / |/ // /
 / ,<  / / /|   // /___
/_/|_|/_/ /_/|_//_____/

Knowledge Retention Library
EOF
}

main() {
    print_banner
    echo ""

    print_info "Starting KNL installation..."
    echo ""

    # Extract minimum Python version from pyproject.toml
    extract_python_version
    echo ""

    # Find compatible Python
    find_python

    # Install UV if needed
    if ! check_uv; then
        echo ""
        read -p "UV is required. Install it now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_uv
        else
            print_error "UV is required to install KNL. Aborting."
            exit 1
        fi
    fi

    echo ""

    # Install KNL
    install_knl

    # Setup PATH
    setup_path

    # Create initial configuration
    create_initial_config

    echo ""
    print_success "KNL installed successfully!"
    echo ""
    print_info "Python used: $PYTHON_CMD ($(get_python_version "$PYTHON_CMD"))"
    echo ""
    print_info "Next steps:"
    echo "  1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo "  2. Navigate to a repository"
    echo "  3. Initialize KNL: knl init"
    echo "  4. Create a task: knl create TASK-123"
    echo "  5. Get help: knl --help"
    echo ""
    print_info "For more information, visit: ${REPO_URL}"
    echo ""
}

# Run main function
main "$@"
