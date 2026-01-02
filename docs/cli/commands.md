# CLI Commands Reference

This documentation is auto-generated from CLI help text.

**Do not edit manually** - run `knl docs sync` to update.


## Overview

Knowledge Retention Library - AI-powered development assistant.


## Core Commands

### `knl init`

Initialize KNL in the current repository. Sets up the .knowledge directory structure and configuration.

```bash
knl init
```

**Options:**

- `--force` - Reinitialize even if already initialized
- `--format` - Task ID format: jira or github
- `--project` - Project identifier (JIRA project or GitHub repo)


## Task Management

### `knl create`

Create a new task (shortcut for 'knl task create').

```bash
knl create
```

**Options:**

- `task_id` - Task ID (e.g., PROJ-123 or #456)
- `--title` - Task title
- `--fetch` - Fetch metadata from remote (default: `True`)

### `knl list`

List all tasks (shortcut for 'knl task list').

```bash
knl list
```

**Options:**

- `--status` - Filter by status
- `--all` - Include archived tasks

### `knl show`

Show task details (shortcut for 'knl task show').

```bash
knl show
```

**Options:**

- `task_id` - Task ID to show

### `knl delete`

Delete a task (shortcut for 'knl task delete').

```bash
knl delete
```

**Options:**

- `task_id` - Task ID to delete
- `--force` - Skip confirmation

#### `knl task` - Command Group

Manage development tasks

See subcommands below.

### `knl task create`

Create a new task.

```bash
knl task create
```

**Options:**

- `task_id` - Task ID (e.g., PROJ-123 or #456)
- `--title` - Task title
- `--fetch` - Fetch metadata from remote (default: `True`)

### `knl task delete`

Delete a task.

```bash
knl task delete
```

**Options:**

- `task_id` - Task ID to delete
- `--force` - Skip confirmation

### `knl task list`

List all tasks.

```bash
knl task list
```

**Options:**

- `--status` - Filter by status
- `--all` - Include archived tasks

### `knl task show`

Show task details.

```bash
knl task show
```

**Options:**

- `task_id` - Task ID to show

### `knl task update`

Update task metadata.

```bash
knl task update
```

**Options:**

- `task_id` - Task ID to update
- `--status` - Update status
- `--title` - Update title


## Configuration

#### `knl config` - Command Group

Manage configuration

See subcommands below.

### `knl config edit`

Open configuration file in editor.

```bash
knl config edit
```

**Options:**

- `--local` - Edit local config

### `knl config get`

Get a configuration value.

```bash
knl config get
```

**Options:**

- `key` - Configuration key (dot notation, e.g., 'task.id_format')
- `--local` - Get local config only

### `knl config list`

List all configuration values.

```bash
knl config list
```

**Options:**

- `--local` - Show local config only
- `--global` - Show global config only

### `knl config set`

Set a configuration value.

```bash
knl config set
```

**Options:**

- `key` - Configuration key (dot notation)
- `value` - Value to set
- `--local` - Set in local config


## Knowledge Management

#### `knl crumb` - Command Group

Browse and manage knowledge crumbs

See subcommands below.

### `knl crumb categories`

List all available categories.

```bash
knl crumb categories
```

**Options:**

- `--describe` - Show category descriptions

### `knl crumb find`

Find crumbs by searching content and metadata.

```bash
knl crumb find
```

**Options:**

- `query` - Search query
- `--in` - Search in: title, description, tags, content
- `--case-sensitive` - Case-sensitive search

### `knl crumb info`

Display metadata about a crumb.

```bash
knl crumb info
```

**Options:**

- `crumb_path` - Crumb path
- `--json` - Output as JSON

### `knl crumb list`

List all available crumbs with optional filtering.

```bash
knl crumb list
```

**Options:**

- `--category` - Filter by category
- `--tag` - Filter by tag (can specify multiple)
- `--difficulty` - Filter by difficulty
- `--sort` - Sort by: title, created, updated, difficulty, category (default: `category`)
- `--format` - Output format: table, compact, json (default: `table`)

### `knl crumb show`

Show the full content of a crumb.

```bash
knl crumb show
```

**Options:**

- `crumb_path` - Crumb path (e.g., devops/github-pages-setup)
- `--line-numbers` - Show line numbers
- `--raw` - Show raw markdown without rendering

### `knl crumb tags`

List all available tags.

```bash
knl crumb tags
```

**Options:**

- `--sort` - Sort by: name, count (default: `name`)
- `--filter` - Filter tags containing text


## Documentation

#### `knl docs` - Command Group

Documentation checking and synchronization

See subcommands below.

### `knl docs check`

Check documentation coverage for CLI commands.

```bash
knl docs check
```

**Options:**

- `--verbose` - Show detailed information
- `--json` - Output results as JSON

### `knl docs dump`

Dump CLI help information as JSON.

```bash
knl docs dump
```

**Options:**

- `--output` - Output file (default: stdout)

### `knl docs sync`

Extract CLI help and sync to documentation.

```bash
knl docs sync
```

**Options:**

- `--verify-only` - Check sync without updating files
- `--output` - Output file (default: docs/cli/commands.md)
