# Configuration

KNL uses a hierarchical configuration system with TOML files.

## Configuration Hierarchy

Settings are loaded in this order (later overrides earlier):

1. **Defaults** - Built-in defaults
2. **Global Config** - `~/.cache/knl/config.toml` (XDG-compliant)
3. **Local Config** - `.knowledge/config.toml` (repository-specific)
4. **CLI Flags** - Command-line arguments

## Configuration Locations

### Global Configuration

```
~/.cache/knl/config.toml
# or
$XDG_CACHE_HOME/knl/config.toml
```

Used for:
- Default task ID format
- Integration credentials
- Global preferences

### Local Configuration

```
<repo>/.knowledge/config.toml
```

Used for:
- Repository-specific settings
- Override global defaults
- Project-specific integrations

## Configuration File Format

```toml
# KNL Configuration

[task]
id_format = "jira"              # or "github"
jira_project = "PROJ"           # JIRA project code
github_repo = "owner/repo"      # GitHub repository
auto_detect_from_branch = true  # Auto-detect task ID from branch name

[integrations.jira]
enabled = false
url = ""
project = ""
username = ""
api_token = ""

[integrations.github]
enabled = false
repo = ""
token = ""

[integrations.ai]
enabled = true
provider = "claude"
model = "claude-sonnet-4-5-20250929"
api_key = ""                    # Optional - uses Claude Code by default

# Display settings
color_output = true
verbose = false
```

## Managing Configuration

### View Configuration

```bash
# View all settings
knl config list

# View local settings only
knl config list --local

# Get specific value
knl config get task.id_format
knl config get integrations.jira.url
```

### Update Configuration

```bash
# Set globally
knl config set task.id_format "github"
knl config set integrations.jira.url "https://company.atlassian.net"

# Set locally (repo-specific)
knl config set task.jira_project "MYPROJ" --local
knl config set color_output false --local
```

### Edit Configuration Files

```bash
# Edit global config in your $EDITOR
knl config edit

# Edit local config
knl config edit --local
```

## Common Configuration Scenarios

### JIRA Project

```toml
[task]
id_format = "jira"
jira_project = "MYPROJ"
auto_detect_from_branch = true

[integrations.jira]
enabled = true
url = "https://company.atlassian.net"
project = "MYPROJ"
username = "your-email@company.com"
api_token = "your-jira-api-token"
```

### GitHub Project

```toml
[task]
id_format = "github"
github_repo = "owner/repo"
auto_detect_from_branch = true

[integrations.github]
enabled = true
repo = "owner/repo"
token = "ghp_your_github_token"
```

### Multiple Projects

Use local configuration for each repository:

```bash
# In project A
cd ~/projects/project-a
knl init
knl config set task.jira_project "PROJA" --local

# In project B
cd ~/projects/project-b
knl init
knl config set task.jira_project "PROJB" --local
```

## Environment Variables

Override configuration with environment variables:

```bash
# Prefix with KNL_
export KNL_TASK_ID_FORMAT=github
export KNL_INTEGRATIONS_JIRA_URL=https://company.atlassian.net
export KNL_COLOR_OUTPUT=true

# Run KNL
knl list
```

## Configuration Reference

### Task Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `task.id_format` | string | `"jira"` | Task ID format: "jira" or "github" |
| `task.jira_project` | string | `""` | JIRA project code |
| `task.github_repo` | string | `""` | GitHub repository |
| `task.auto_detect_from_branch` | boolean | `true` | Auto-detect task ID from git branch |

### JIRA Integration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `integrations.jira.enabled` | boolean | `false` | Enable JIRA integration |
| `integrations.jira.url` | string | `""` | JIRA instance URL |
| `integrations.jira.project` | string | `""` | Default JIRA project |
| `integrations.jira.username` | string | `""` | JIRA username/email |
| `integrations.jira.api_token` | string | `""` | JIRA API token |

### GitHub Integration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `integrations.github.enabled` | boolean | `false` | Enable GitHub integration |
| `integrations.github.repo` | string | `""` | GitHub repository |
| `integrations.github.token` | string | `""` | GitHub personal access token |

### AI Integration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `integrations.ai.enabled` | boolean | `true` | Enable AI features |
| `integrations.ai.provider` | string | `"claude"` | AI provider |
| `integrations.ai.model` | string | `"claude-sonnet-4-5-20250929"` | Model to use |
| `integrations.ai.api_key` | string | `""` | API key (optional with Claude Code) |

### Display Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `color_output` | boolean | `true` | Enable colored terminal output |
| `verbose` | boolean | `false` | Enable verbose logging |

## Next Steps

- [Task Management Guide](guide/tasks.md) - Learn about task workflows
- [Git Integration](guide/git.md) - Integrate with git workflows
- [CLI Reference](cli/commands.md) - Complete command documentation
