# KNL Crumbs

This directory contains **crumbs** - carefully collated pieces of knowledge about development tasks, patterns, and solutions. Think of them as bite-sized, reusable knowledge articles that capture best practices and lessons learned.

## What Are Crumbs?

Crumbs are:
- ✅ **Actionable** - Step-by-step guides you can follow
- ✅ **Tested** - Verified solutions to real problems
- ✅ **Reusable** - Applicable across multiple projects
- ✅ **Self-contained** - Each crumb covers one topic completely
- ✅ **LLM-friendly** - Structured with YAML metadata for AI agents

Crumbs are NOT:
- ❌ Templates (boilerplate code to copy-paste)
- ❌ API documentation (that belongs in code comments)
- ❌ Project-specific notes (use `.knowledge/` for those)
- ❌ General tutorials (these are focused solutions)

## Directory Structure

```
crumbs/
├── README.md                    # This file
└── crumbs/
    ├── devops/                  # DevOps, CI/CD, deployment
    │   └── github-pages-setup.md
    ├── development/             # Development practices, patterns
    ├── testing/                 # Testing strategies, tools
    ├── security/                # Security best practices
    └── tooling/                 # Tool configuration, usage
```

### Categories

Crumbs are organized by category:

- **devops/** - CI/CD, deployment, infrastructure, automation
- **development/** - Coding patterns, practices, workflows
- **testing/** - Testing strategies, frameworks, debugging
- **security/** - Security practices, vulnerability fixes
- **tooling/** - Tool setup, configuration, optimization

## Crumb Format

Each crumb is a Markdown file with YAML frontmatter:

```markdown
---
title: "Clear, Descriptive Title"
description: "One-line summary of what this crumb covers"
category: "devops"
tags: ["tag1", "tag2", "tag3"]
difficulty: "beginner|intermediate|advanced"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Author Name"
related: ["../other/crumb.md"]
prerequisites:
  - "Required knowledge or setup"
  - "Another prerequisite"
applies_to:
  - "Technology or framework"
  - "Use case or scenario"
---

# Title

Content in GitHub Flavored Markdown...
```

### Required Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `title` | Clear, descriptive title | "GitHub Pages Setup with GitHub Actions" |
| `description` | One-line summary | "Step-by-step guide for configuring GitHub Pages deployment" |
| `category` | Crumb category (matches directory) | "devops" |
| `tags` | List of searchable tags | ["github", "deployment", "ci-cd"] |
| `difficulty` | Target audience level | "beginner", "intermediate", "advanced" |
| `created` | Date crumb was created | "2025-12-29" |
| `updated` | Date of last update | "2025-12-29" |
| `author` | Original author | "Claude Sonnet 4.5" |
| `related` | Links to related crumbs | ["../testing/e2e-setup.md"] |
| `prerequisites` | Required knowledge/setup | ["GitHub repository with admin access"] |
| `applies_to` | Technologies/scenarios | ["MkDocs", "Jekyll", "Hugo"] |

## Using Crumbs

### For Humans

1. **Browse by category** in `crumbs/` subdirectories
2. **Search by tag** using grep or your IDE
3. **Follow prerequisites** before starting
4. **Check "applies_to"** to verify relevance
5. **Reference from tasks** in your `.knowledge/tasks/` notes

### For AI Agents

Crumbs are structured for LLM consumption:
- **YAML frontmatter** provides structured metadata
- **GFM formatting** is well-supported by LLMs
- **Self-contained** content minimizes context needs
- **Clear sections** help extraction of specific info
- **Code examples** are properly fenced and labeled

Example prompt for AI:
```
Search the crumbs/ directory for information about
GitHub Pages deployment. Use the YAML metadata to find relevant
crumbs and extract the setup steps.
```

## Contributing Crumbs

When you discover a reusable solution or best practice:

### 1. Choose the Right Category

Place the crumb in the most appropriate category directory. If unsure:
- **devops/** - Anything related to deployment, CI/CD, infrastructure
- **development/** - Coding patterns, workflows, practices
- **testing/** - Testing approaches, frameworks, debugging
- **security/** - Security fixes, best practices
- **tooling/** - Configuration and optimization of tools

### 2. Create the Crumb File

```bash
# Create file in appropriate category
touch crumbs/devops/my-new-crumb.md
```

### 3. Add YAML Frontmatter

Copy the metadata template and fill in all fields:

```yaml
---
title: "Your Title Here"
description: "One-line description"
category: "devops"
tags: ["relevant", "tags", "here"]
difficulty: "beginner"
created: "2025-12-29"
updated: "2025-12-29"
author: "Claude Sonnet 4.5"
related: []
prerequisites:
  - "What's needed before starting"
applies_to:
  - "What this applies to"
---
```

### 4. Write the Content

Use GitHub Flavored Markdown:

- ✅ Clear sections with `##` headers
- ✅ Code blocks with language tags: ` ```yaml `
- ✅ Task lists: `- [ ] Todo item`
- ✅ Tables for comparisons
- ✅ Alerts: `> **Note:** Important info`
- ✅ Links to related crumbs and external resources

Structure suggestion:
1. **Use Case** - When to use this crumb
2. **Prerequisites** - What you need first
3. **Steps** - Numbered, actionable instructions
4. **Common Issues** - Problems and solutions
5. **Example** - Complete working example
6. **Verification** - How to test it worked
7. **Related Resources** - Links for more info

### 5. Test the Crumb

Before committing:
- ✅ Follow your own instructions from scratch
- ✅ Verify all code examples work
- ✅ Check links aren't broken
- ✅ Ensure YAML frontmatter is valid
- ✅ Proofread for clarity

### 6. Commit and Share

```bash
git add crumbs/category/your-crumb.md
git commit -m "Add crumb: Brief description"
```

## Quality Guidelines

Good crumbs are:

1. **Focused** - One topic, covered completely
2. **Actionable** - Reader can follow and succeed
3. **Tested** - Steps have been verified to work
4. **Current** - Updated when tools/practices change
5. **Clear** - Written for the target difficulty level
6. **Complete** - Includes troubleshooting and verification
7. **Referenced** - Links to official docs and related crumbs

## Maintenance

Crumbs should be:
- **Reviewed** when technologies update
- **Updated** when better approaches emerge
- **Deprecated** when no longer relevant (mark in frontmatter)
- **Linked** when new related crumbs are added

## Integration with KNL

Crumbs at repository root (`crumbs/`) are:
- **Version controlled** - Part of the KNL project
- **Shared across projects** - Reusable knowledge
- **AI-accessible** - Structured for LLM consumption

Project-specific knowledge goes in:
- **`.knowledge/`** - Local, gitignored development context
- **`.knowledge/tasks/`** - Task-specific notes and context
- **`.knowledge/templates/`** - Local customized templates

Users can copy crumbs from `crumbs/` to their project's `.knowledge/` for customization.

## Examples

See existing crumbs for examples:
- [`devops/github-pages-setup.md`](crumbs/devops/github-pages-setup.md) - Complete guide with all sections

## Related

- [KNL Documentation](https://akaliazin.github.io/knl/)
- [PRINCIPLES.md](../PRINCIPLES.md) - KNL architecture principles
- [CLAUDE.md](../CLAUDE.md) - Instructions for Claude Code
