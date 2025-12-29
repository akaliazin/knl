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

## Next Steps

- [Task Management Guide](tasks.md) - Learn about working with tasks
- [Configuration](../configuration.md) - Configure knowledge retention
- [Architecture Principles](../architecture/principles.md) - Understand the design
