# Knowledge Base

*This page is under construction.*

The Knowledge Base is the heart of KNL's retention system, storing task context, learned patterns, and development standards.

## Overview

The `.knowledge/` directory stores:

- **Task Context**: Markdown files with development notes
- **Templates**: Reusable task templates
- **Standards**: Evolving development standards
- **Scripts**: Repository-specific automation

## Directory Structure

```
.knowledge/
├── config.toml           # Local configuration
├── cache/                # Local cache
├── tasks/                # Task storage
│   └── TASK-ID/
│       ├── metadata.json
│       ├── context.md
│       ├── tests/
│       └── artifacts/
├── templates/            # Task templates
├── standards/            # Development standards
└── scripts/              # Helper scripts
```

## Features

### Task Context Retention

Each task maintains its own context file where you can document:
- Implementation decisions
- Challenges encountered
- Solutions discovered
- Learnings for future reference

### Development Standards

The `standards/development.md` file evolves as you work:
- Coding conventions
- Testing requirements
- Documentation patterns
- Best practices learned from tasks

### Knowledge Transfer

Export knowledge to new projects:
- Templates for common task types
- Learned best practices
- Development standards
- Custom scripts

## Knowledge Crumbs

In addition to the task-based knowledge you accumulate in `.knowledge/`, KNL provides **curated knowledge crumbs** - bite-sized, reusable guides for common development tasks.

### What Are Crumbs?

Knowledge crumbs are:

- **Curated**: Carefully written and tested solutions to common development problems
- **Categorized**: Organized by category (DevOps, Testing, Security, Development, Tooling)
- **LLM-friendly**: Structured with YAML frontmatter metadata for easy AI consumption
- **Self-contained**: Each crumb is complete and actionable on its own
- **Searchable**: Full-text search with filtering and sorting capabilities

### Crumb Locations

Crumbs are automatically deployed during KNL installation:

**Repo-local installation:**
```
.knl/know-how/crumbs/
├── devops/
│   └── github-pages-setup.md
├── development/
├── testing/
├── security/
└── tooling/
```

**User-local installation:**
```
~/.local/knl/know-how/crumbs/
├── devops/
├── development/
├── testing/
├── security/
└── tooling/
```

### Using the Crumb CLI

KNL provides a complete CLI for browsing and searching crumbs:

```bash
# List all crumbs
knl crumb list

# Filter by category
knl crumb list --category devops

# Filter by tags and difficulty
knl crumb list --tag deployment --difficulty beginner

# Sort by updated date
knl crumb list --sort updated

# Show crumb content with rich rendering
knl crumb show devops/github-pages-setup

# Show crumb metadata only
knl crumb info devops/github-pages-setup

# Search crumbs
knl crumb find "github actions"
knl crumb find "deployment" --in title

# Browse categories
knl crumb categories --describe

# Browse tags
knl crumb tags --sort count
```

### Crumb Metadata

Each crumb includes comprehensive metadata:

```yaml
---
title: "Descriptive Title"
description: "One-line summary"
category: "devops"
tags: ["tag1", "tag2"]
difficulty: "beginner"  # beginner | intermediate | advanced
created: "2025-12-31"
updated: "2025-12-31"
author: "Author Name"
related: ["other/crumb"]
prerequisites:
  - "Prerequisite 1"
applies_to:
  - "Technology 1"
---
```

This metadata enables:
- **Filtering**: Find crumbs by category, tags, or difficulty
- **Discovery**: Browse related crumbs
- **Context**: Understand prerequisites and applicability
- **AI Integration**: LLMs can easily parse and use crumbs

### Crumbs vs Task Knowledge

**Crumbs** (`.knl/know-how/crumbs/`):
- Pre-written, curated guides
- General purpose, reusable across projects
- Deployed with KNL installation
- Read-only reference material

**Task Knowledge** (`.knowledge/tasks/`):
- Project-specific context
- Grows as you work on tasks
- Created by you during development
- Evolves with your project

Both systems complement each other: crumbs provide foundational knowledge, while task context captures project-specific learnings.

### Contributing Crumbs

Want to add your own crumbs? See the [know-how README](https://github.com/akaliazin/knl/blob/main/know-how/README.md) for the crumb format and contribution guidelines.

## Next Steps

- [Crumb CLI Reference](../cli/crumbs.md) - Complete crumb command documentation
- [Task Management Guide](tasks.md) - Learn about working with tasks
- [Configuration](../configuration.md) - Configure knowledge retention
- [Architecture Principles](../architecture/principles.md) - Understand the design
