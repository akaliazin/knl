# CLI Commands Reference

*This page is under construction.*

Complete reference for all KNL CLI commands.

## Global Commands

### `knl init`

Initialize KNL in the current repository.

```bash
knl init
```

**What it does:**
- Creates `.knowledge/` directory structure
- Creates initial configuration
- Sets up task templates
- Creates `standards/development.md`
- Updates `.gitignore`

**Options:**
- `--force` - Reinitialize even if already initialized

### `knl version`

Display KNL version information.

```bash
knl version
knl --version
```

### `knl help`

Display help information.

```bash
knl help
knl --help
knl <command> --help
```

## Task Management

See [Task Commands](tasks.md) for detailed task management commands.

### `knl create`

Create a new task.

```bash
knl create PROJ-123
knl create "#456"
knl create PROJ-123 --title "Implement feature"
```

### `knl list`

List all tasks.

```bash
knl list
knl list --status in_progress
knl list --format json
```

### `knl show`

Show task details.

```bash
knl show PROJ-123
knl show "#456"
```

### `knl task update`

Update task status or metadata.

```bash
knl task update PROJ-123 --status in_progress
knl task update PROJ-123 --title "New title"
```

### `knl delete`

Delete a task.

```bash
knl delete PROJ-123
knl delete PROJ-123 --force
```

## Configuration

See [Config Commands](config.md) for detailed configuration commands.

### `knl config list`

List all configuration values.

```bash
knl config list
knl config list --global
knl config list --local
```

### `knl config get`

Get a configuration value.

```bash
knl config get task.id_format
knl config get integrations.jira.url
```

### `knl config set`

Set a configuration value.

```bash
knl config set integrations.jira.url "https://company.atlassian.net"
knl config set task.default_status "todo" --local
```

## Command Aliases

Some commands have shorter aliases:

```bash
knl create    # Also: knl task create
knl list      # Also: knl task list
knl show      # Also: knl task show
```

## Output Formats

Most commands support multiple output formats:

```bash
knl list --format table   # Default
knl list --format json
knl list --format yaml
```

## Exit Codes

KNL uses standard exit codes:

- `0` - Success
- `1` - General error
- `2` - Invalid usage
- `3` - Task not found
- `4` - Configuration error

## Next Steps

- [Task Commands](tasks.md) - Detailed task command reference
- [Config Commands](config.md) - Detailed config command reference
- [Task Management Guide](../guide/tasks.md) - Task management workflows
