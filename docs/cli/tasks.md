# Task Commands Reference

*This page is under construction.*

Detailed reference for task management commands.

## Creating Tasks

### `knl create`

Create a new task with the specified ID.

```bash
# JIRA task
knl create PROJ-123

# GitHub issue
knl create "#456"

# With title
knl create PROJ-123 --title "Implement user authentication"

# With status
knl create PROJ-123 --status in_progress
```

**Arguments:**
- `task-id` - Task identifier (JIRA format: `PROJ-123` or GitHub format: `#456`)

**Options:**
- `--title TEXT` - Task title
- `--status STATUS` - Initial status (default: `todo`)
- `--force` - Overwrite existing task

**Created Structure:**
```
.knowledge/tasks/PROJ-123/
├── metadata.json
├── context.md
├── tests/
└── artifacts/
```

## Listing Tasks

### `knl list`

List all tasks in the repository.

```bash
# List all tasks
knl list

# Filter by status
knl list --status in_progress
knl list --status done

# Different formats
knl list --format table
knl list --format json
```

**Options:**
- `--status STATUS` - Filter by status (todo, in_progress, in_review, done)
- `--format FORMAT` - Output format (table, json, yaml)
- `--sort FIELD` - Sort by field (created, updated, status)

## Viewing Tasks

### `knl show`

Show detailed information about a task.

```bash
knl show PROJ-123
knl show "#456"
```

**Displays:**
- Task metadata (ID, title, status, dates)
- Context summary
- Test files
- Artifacts

## Updating Tasks

### `knl task update`

Update task metadata or status.

```bash
# Update status
knl task update PROJ-123 --status in_progress
knl task update PROJ-123 --status done

# Update title
knl task update PROJ-123 --title "New title"

# Multiple updates
knl task update PROJ-123 --status in_review --title "Ready for review"
```

**Options:**
- `--status STATUS` - Update status
- `--title TEXT` - Update title

**Valid Statuses:**
- `todo` - Not started
- `in_progress` - Currently working
- `in_review` - Ready for review
- `done` - Completed

## Deleting Tasks

### `knl delete`

Delete a task.

```bash
# Delete with confirmation
knl delete PROJ-123

# Force delete without confirmation
knl delete PROJ-123 --force
```

**Options:**
- `--force` - Skip confirmation prompt

**Warning:** This permanently deletes the task directory and all contents.

## Working with Task Context

### Editing Context

Task context is stored in `context.md`:

```bash
# Open in default editor
$EDITOR .knowledge/tasks/PROJ-123/context.md
```

### Adding Tests

Place test files in the task's `tests/` directory:

```bash
.knowledge/tasks/PROJ-123/tests/
├── test_feature.py
└── test_integration.py
```

### Storing Artifacts

Store task-related artifacts:

```bash
.knowledge/tasks/PROJ-123/artifacts/
├── design.png
├── api_spec.yaml
└── performance_results.json
```

## Task ID Formats

### JIRA Format

Pattern: `^[A-Z][A-Z0-9]+-\d+$`

Examples:
- `PROJ-123`
- `ABC-456`
- `MYPROJECT-789`

### GitHub Format

Pattern: `^#\d+$`

Examples:
- `#123`
- `#456`

**Note:** GitHub IDs are normalized to `gh-123` for filesystem safety.

## Next Steps

- [Task Management Guide](../guide/tasks.md) - Task workflows
- [Commands Reference](commands.md) - All commands
- [Knowledge Base](../guide/knowledge.md) - Knowledge retention
