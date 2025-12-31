# Quick Start Guide

Get up and running with KNL in minutes.

## Step 1: Install KNL

Choose your installation mode:

=== "Repo-Local (Recommended)"

    ```bash
    cd your-project
    curl -LsSf https://akaliazin.github.io/knl/install.sh | sh
    export PATH="$(pwd)/.knl/bin:$PATH"
    ```

=== "User-Local"

    ```bash
    curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --user-local
    # PATH is automatically configured
    ```

=== "Compiled Binary (Portable)"

    ```bash
    # Requires only Python 3.8+, no UV needed
    curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled
    export PATH="$(pwd)/.knl/bin:$PATH"
    ```

Verify installation:

```bash
knl --version
```

## Step 2: Initialize KNL in Your Repository

```bash
cd your-project
knl init
```

You'll be asked:

1. **Task ID format**: Choose `jira` or `github`
2. **Project identifier**: Enter your JIRA project code (e.g., `PROJ`) or GitHub repo (e.g., `owner/repo`)

This creates:

```
your-project/
├── .knl/                # KNL installation (git-ignored)
│   ├── know-how/       # Knowledge crumbs - curated dev knowledge
│   │   └── crumbs/     # Browse for helpful guides!
│   └── bin/            # Wrapper scripts
├── .knowledge/          # Knowledge base (git-ignored)
│   ├── config.toml     # Local settings
│   ├── tasks/          # Task storage
│   ├── templates/      # Task templates
│   └── standards/      # Development standards
└── .gitignore          # Updated to exclude .knl/ and .knowledge/
```

!!! tip "Explore Knowledge Crumbs"
    KNL includes curated development knowledge in `.knl/know-how/crumbs/`.
    These are bite-sized, actionable guides for common tasks like:

    - DevOps: Deployment, CI/CD, infrastructure
    - Testing: Testing strategies, frameworks
    - Security: Security best practices
    - Development: Patterns, workflows

    Browse with: `ls .knl/know-how/crumbs/`

## Step 3: Create Your First Task

### JIRA-Style Task

```bash
knl create PROJ-123
```

### GitHub-Style Task

```bash
knl create "#456"
```

### With Title

```bash
knl create PROJ-123 --title "Add user authentication"
```

This creates a task directory:

```
.knowledge/tasks/PROJ-123/
├── metadata.json       # Task metadata
├── context.md          # Development context
├── tests/             # Task-specific tests
└── artifacts/         # Generated artifacts
```

## Step 4: Work on Your Task

### View Task Details

```bash
knl show PROJ-123
```

Output:
```
Task: PROJ-123
Title: Add user authentication
Status: todo
Created: 2025-12-29 10:30:00

Context: .knowledge/tasks/PROJ-123/context.md
Tests: .knowledge/tasks/PROJ-123/tests/
```

### Update Task Context

Edit the context file as you work:

```bash
# Open in your editor
vim .knowledge/tasks/PROJ-123/context.md
```

Add notes about:
- Implementation approach
- Technical decisions
- Challenges encountered
- Solutions discovered

### Update Task Status

```bash
# Mark as in progress
knl task update PROJ-123 --status in_progress

# Mark as in review
knl task update PROJ-123 --status in_review

# Mark as done
knl task update PROJ-123 --status done
```

## Step 5: List Your Tasks

```bash
# All tasks
knl list

# Filter by status
knl list --status in_progress

# Include archived tasks
knl list --all
```

## Common Workflows

### Starting a New Feature

```bash
# 1. Create task
knl create PROJ-456 --title "Add dark mode toggle"

# 2. Update status
knl task update PROJ-456 --status in_progress

# 3. Work on implementation
# ... code changes ...

# 4. Update context as you go
echo "## Implementation Notes
- Used CSS variables for theme switching
- Added toggle in settings panel
" >> .knowledge/tasks/PROJ-456/context.md

# 5. Mark complete
knl task update PROJ-456 --status done
```

### Bug Fix Workflow

```bash
# 1. Create bug task
knl create PROJ-789 --title "Fix login timeout issue"

# 2. Document investigation
knl show PROJ-789  # opens context file
# Add: Root cause, reproduction steps, fix approach

# 3. Track testing
mkdir .knowledge/tasks/PROJ-789/tests
# Add test files

# 4. Complete
knl task update PROJ-789 --status done
```

### Managing Multiple Tasks

```bash
# List active work
knl list --status in_progress

# Switch between tasks
knl show PROJ-123
knl show PROJ-456

# Archive old tasks
knl task archive PROJ-123
```

## Configuration

### View Current Settings

```bash
# All settings
knl config list

# Local settings only
knl config list --local

# Specific value
knl config get task.id_format
```

### Update Settings

```bash
# Set globally
knl config set integrations.jira.url "https://company.atlassian.net"

# Set locally (repo-specific)
knl config set task.jira_project "MYPROJ" --local
```

### Edit Config Files

```bash
# Edit global config
knl config edit

# Edit local config
knl config edit --local
```

## Tips & Best Practices

### 1. Keep Context Updated

Update `.knowledge/tasks/<TASK-ID>/context.md` as you work:
- Before starting: Document your plan
- During work: Note decisions and blockers
- After completion: Summarize what was learned

### 2. Use Descriptive Task Titles

```bash
# Good
knl create PROJ-123 --title "Add OAuth2 authentication to API"

# Less helpful
knl create PROJ-123 --title "Fix auth"
```

### 3. Organize Tests by Task

Keep task-specific tests in `.knowledge/tasks/<TASK-ID>/tests/`:
```bash
.knowledge/tasks/PROJ-123/tests/
├── test_authentication.py
├── test_oauth_flow.py
└── fixtures/
```

### 4. Leverage Standards

KNL creates `.knowledge/standards/development.md` - use it to:
- Document coding conventions
- Define testing requirements
- Establish git workflows

### 5. Browse Knowledge Crumbs

Explore curated development knowledge:
```bash
# List available crumbs
ls .knl/know-how/crumbs/

# Read a crumb
cat .knl/know-how/crumbs/devops/github-pages-setup.md

# Search for specific topics
grep -r "deployment" .knl/know-how/crumbs/
```

Crumbs are LLM-friendly with YAML metadata, making them perfect for AI-assisted development.

### 6. Regular Task Reviews

Periodically review completed tasks:
```bash
knl list --status done | tail -10
```

Extract patterns and update standards accordingly.

## Next Steps

- [Task Management Guide](guide/tasks.md) - Deep dive into task features
- [Configuration Guide](configuration.md) - Advanced configuration options
- [Knowledge Base](guide/knowledge.md) - Understand the knowledge system
- [CLI Reference](cli/commands.md) - Complete command documentation
