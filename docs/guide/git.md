# Git Integration

*This page is under construction.*

KNL integrates with git workflows to enhance task tracking and development processes.

## Features

### Task ID Auto-Detection

KNL can automatically detect task IDs from git branch names:

```bash
# Create branch with task ID
git checkout -b feature/PROJ-123-user-auth

# KNL detects PROJ-123 from branch name
knl create PROJ-123  # Auto-populated from branch
```

Supported patterns:
- `feature/PROJ-123-description`
- `bugfix/PROJ-456-description`
- `PROJ-123/description`
- `#456-description` (GitHub issues)

### Git Workflow Integration

Track tasks alongside git operations:

```bash
# Start new task
git checkout -b feature/PROJ-123-new-feature
knl create PROJ-123 --title "New feature"

# Work on task
# ... make changes ...

# Update task status
knl task update PROJ-123 --status in_progress

# Commit changes
git commit -m "PROJ-123: Implement new feature"

# Complete task
knl task update PROJ-123 --status done
git push origin feature/PROJ-123-new-feature
```

## Planned Features

### Commit Message Generation (Phase 5)

Future versions will support:
- AI-powered commit message generation
- Automatic task ID insertion
- Commit message templates based on task type

### PR Summary Creation (Phase 5)

Automatically generate PR descriptions from:
- Task context
- Commit history
- Code changes
- Test results

### Branch Naming Suggestions (Phase 5)

Smart branch name suggestions based on:
- Task ID and title
- Task type (feature, bugfix, etc.)
- Team conventions

## Configuration

Enable task ID auto-detection:

```toml
[task]
auto_detect_from_branch = true
```

## Next Steps

- [Task Management Guide](tasks.md) - Learn about task workflows
- [Configuration](../configuration.md) - Configure git integration
- [CLI Reference](../cli/commands.md) - Command documentation
