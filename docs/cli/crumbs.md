# Crumb Commands

Browse and manage knowledge crumbs - curated development knowledge deployed with KNL.

## Overview

Knowledge crumbs are bite-sized, actionable guides for common development tasks. They are:

- **Curated**: Carefully written and tested solutions
- **Categorized**: Organized by DevOps, Testing, Security, Development, Tooling
- **LLM-friendly**: Structured with YAML frontmatter metadata
- **Self-contained**: Each crumb is complete and actionable
- **Searchable**: Full-text search with filtering

## Command: `knl crumb list`

List all available crumbs with optional filtering and sorting.

### Usage

```bash
knl crumb list [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--category TEXT` | `-c` | Filter by category |
| `--tag TEXT` | `-t` | Filter by tag (can specify multiple) |
| `--difficulty TEXT` | `-d` | Filter by difficulty (beginner, intermediate, advanced) |
| `--sort TEXT` | | Sort by: title, created, updated, difficulty, category (default: category) |
| `--format TEXT` | | Output format: table, compact, json (default: table) |

### Examples

```bash
# List all crumbs
knl crumb list

# List DevOps crumbs
knl crumb list --category devops

# List crumbs tagged with deployment
knl crumb list --tag deployment

# List beginner-level crumbs
knl crumb list --difficulty beginner

# Sort by most recently updated
knl crumb list --sort updated

# Combine filters
knl crumb list --category devops --difficulty beginner --sort title

# Get JSON output
knl crumb list --format json

# Compact output (just paths)
knl crumb list --format compact
```

### Output

Table format shows:
- Category
- Title
- Difficulty level
- Last updated date
- Tags (truncated if many)

---

## Command: `knl crumb show`

Display the full content of a crumb with rich markdown rendering.

### Usage

```bash
knl crumb show <crumb-path> [OPTIONS]
```

### Arguments

- `<crumb-path>` - Relative path to crumb (e.g., `devops/github-pages-setup`)

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--line-numbers` | `-n` | Show line numbers |
| `--raw` | | Show raw markdown without rendering |

### Examples

```bash
# Show crumb with rich rendering
knl crumb show devops/github-pages-setup

# Show with line numbers
knl crumb show devops/github-pages-setup --line-numbers

# Show raw markdown
knl crumb show devops/github-pages-setup --raw
```

### Output

Displays:
- Crumb title and path
- Beautifully rendered markdown content
- Syntax-highlighted code blocks
- File location at bottom

---

## Command: `knl crumb info`

Display metadata about a crumb without showing the full content.

### Usage

```bash
knl crumb info <crumb-path> [OPTIONS]
```

### Arguments

- `<crumb-path>` - Relative path to crumb

### Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |

### Examples

```bash
# Show crumb metadata
knl crumb info devops/github-pages-setup

# Get JSON output
knl crumb info devops/github-pages-setup --json
```

### Output

Shows all metadata fields:
- Title
- Description
- Category
- Difficulty
- Created and updated dates
- Author
- Tags
- Prerequisites
- Applies to (technologies/scenarios)
- Related crumbs
- File location

---

## Command: `knl crumb find`

Search crumbs by content and metadata.

### Usage

```bash
knl crumb find <query> [OPTIONS]
```

### Arguments

- `<query>` - Search query text

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--in TEXT` | | Search in specific field: title, description, tags, content |
| `--case-sensitive` | `-s` | Case-sensitive search |

### Examples

```bash
# Search all fields for "deployment"
knl crumb find deployment

# Search only in titles
knl crumb find "github" --in title

# Search in descriptions
knl crumb find "testing" --in description

# Search tags
knl crumb find "ci-cd" --in tags

# Search content
knl crumb find "workflow" --in content

# Case-sensitive search
knl crumb find "GitHub" --case-sensitive
```

### Output

Shows matching crumbs in table format with the number of matches found.

---

## Command: `knl crumb categories`

List all available categories with crumb counts.

### Usage

```bash
knl crumb categories [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--describe` | `-d` | Show category descriptions |

### Examples

```bash
# List categories
knl crumb categories

# List with descriptions
knl crumb categories --describe
```

### Output

Table showing:
- Category name
- Number of crumbs in category
- Description (if `--describe` flag used)
- Total count summary

### Built-in Categories

- **devops** - DevOps, CI/CD, deployment, infrastructure
- **development** - Development practices, patterns, workflows
- **testing** - Testing strategies, frameworks, debugging
- **security** - Security best practices, vulnerability fixes
- **tooling** - Tool configuration, usage, optimization

---

## Command: `knl crumb tags`

List all available tags with usage counts.

### Usage

```bash
knl crumb tags [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--sort TEXT` | Sort by: name, count (default: name) |
| `--filter TEXT` | Filter tags containing text |

### Examples

```bash
# List all tags
knl crumb tags

# Sort by most used
knl crumb tags --sort count

# Filter tags containing "github"
knl crumb tags --filter github
```

### Output

Table showing:
- Tag name
- Number of crumbs using this tag
- Total unique tags count

---

## Crumb Locations

Crumbs are automatically deployed during KNL installation to:

**Repo-local installation:**
```
.knl/know-how/crumbs/
```

**User-local installation:**
```
~/.local/knl/know-how/crumbs/
```

## Crumb File Format

Crumbs are markdown files with YAML frontmatter:

```markdown
---
title: "Descriptive Title"
description: "One-line summary"
category: "devops"
tags: ["tag1", "tag2"]
difficulty: "beginner"
created: "2025-12-31"
updated: "2025-12-31"
author: "Author Name"
related: []
prerequisites:
  - "Prerequisite 1"
  - "Prerequisite 2"
applies_to:
  - "Technology 1"
  - "Use case 2"
---

# Content

Markdown content goes here...
```

## Tips

1. **Browse by category** to discover crumbs in your area of interest
2. **Use tags** to find crumbs about specific technologies
3. **Search content** to find solutions to specific problems
4. **Check metadata** before diving into a crumb to see if it applies to your situation
5. **JSON output** can be piped to other tools: `knl crumb list --format json | jq`

## Related Commands

- [`knl --help`](commands.md) - Main CLI help
- [`knl task`](tasks.md) - Task management commands
- [`knl config`](config.md) - Configuration commands

## Next Steps

- [Knowledge Base Guide](../guide/knowledge.md) - Understanding KNL's knowledge system
- [Contributing Crumbs](https://github.com/akaliazin/knl/blob/main/know-how/README.md) - How to add new crumbs
