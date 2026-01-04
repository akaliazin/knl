# Git Hooks for KNL Development

This directory contains git hooks to automate common development tasks.

## Available Hooks

### `pre-commit`

Automatically syncs `install.sh` to `docs/install.sh` when committing changes to the installer.

**What it does:**
- Detects if `install.sh` is being committed
- Copies `install.sh` to `docs/install.sh`
- Sets executable permissions
- Stages `docs/install.sh` for the same commit

**Why needed:**
- GitHub Pages serves from the `docs/` directory via MkDocs
- Users download installer from `https://akaliazin.github.io/knl/install.sh`
- Without this hook, `docs/install.sh` can become outdated
- Manual syncing is error-prone

## Installation

Run the install script from the repository root:

```bash
./hooks/install.sh
```

This will copy the hooks to `.git/hooks/` and make them executable.

## Uninstallation

To remove the hooks:

```bash
rm .git/hooks/pre-commit
```

## Manual Sync (if hook not installed)

If you haven't installed the hook and need to sync manually:

```bash
cp install.sh docs/install.sh
chmod +x docs/install.sh
git add docs/install.sh
```

## Skipping Hooks

If you need to skip the pre-commit hook for a specific commit:

```bash
git commit --no-verify
```

**Note:** Only use `--no-verify` if you have a specific reason to skip the sync.
