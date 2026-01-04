#!/usr/bin/env bash
# Install git hooks for KNL development

set -e

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_HOOKS_DIR="$(git rev-parse --git-dir)/hooks"

echo "Installing KNL git hooks..."

# Install pre-commit hook
if [ -f "$HOOKS_DIR/pre-commit" ]; then
    cp "$HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
    chmod +x "$GIT_HOOKS_DIR/pre-commit"
    echo "✓ Installed pre-commit hook (syncs install.sh → docs/install.sh)"
fi

echo ""
echo "Git hooks installed successfully!"
echo "The pre-commit hook will automatically keep docs/install.sh in sync."
