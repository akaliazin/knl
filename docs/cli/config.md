# Config Commands Reference

*This page is under construction.*

Detailed reference for configuration management commands.

## Listing Configuration

### `knl config list`

List all configuration values.

```bash
# List all config (merged global + local)
knl config list

# List only global config
knl config list --global

# List only local config
knl config list --local

# Output as JSON
knl config list --format json
```

**Options:**
- `--global` - Show only global configuration
- `--local` - Show only local configuration
- `--format FORMAT` - Output format (table, json, yaml)

## Getting Configuration

### `knl config get <key>`

Get a specific configuration value.

```bash
# Get single value
knl config get task.id_format
knl config get integrations.jira.url

# Get from specific scope
knl config get task.id_format --global
knl config get task.id_format --local
```

**Arguments:**
- `key` - Configuration key in dot notation

**Options:**
- `--global` - Get from global config only
- `--local` - Get from local config only

## Setting Configuration

### `knl config set <key> <value>`

Set a configuration value.

```bash
# Set in merged config (default: global)
knl config set task.id_format "jira"

# Set in global config explicitly
knl config set integrations.jira.url "https://company.atlassian.net" --global

# Set in local config
knl config set task.default_status "in_progress" --local
```

**Arguments:**
- `key` - Configuration key in dot notation
- `value` - Configuration value

**Options:**
- `--global` - Set in global config
- `--local` - Set in local config (default if in repository)

## Unsetting Configuration

### `knl config unset <key>`

Remove a configuration value.

```bash
# Unset from global config
knl config unset task.id_format --global

# Unset from local config
knl config unset task.default_status --local
```

**Options:**
- `--global` - Unset from global config
- `--local` - Unset from local config

## Configuration Scopes

### Global Configuration

Located at: `~/.cache/knl/config.toml`

```bash
# Edit global config
knl config set integrations.jira.url "https://company.atlassian.net" --global
```

**Use for:**
- User-wide settings
- Integration credentials
- Default preferences

### Local Configuration

Located at: `.knowledge/config.toml`

```bash
# Edit local config
knl config set task.id_format "github" --local
```

**Use for:**
- Repository-specific settings
- Project conventions
- Team standards

## Configuration Keys

### Task Settings

```bash
knl config set task.id_format "jira"           # or "github"
knl config set task.default_status "todo"      # or "in_progress", etc.
knl config set task.auto_detect_from_branch true
```

### Integration Settings

#### JIRA Integration

```bash
knl config set integrations.jira.url "https://company.atlassian.net"
knl config set integrations.jira.username "user@example.com"
knl config set integrations.jira.api_token "your-token"
knl config set integrations.jira.default_project "PROJ"
```

#### GitHub Integration

```bash
knl config set integrations.github.token "ghp_your_token"
knl config set integrations.github.repository "owner/repo"
```

### AI Settings

```bash
knl config set ai.provider "anthropic"
knl config set ai.model "claude-sonnet-4"
knl config set ai.api_key "your-api-key"
```

## Configuration File Format

Configuration files use TOML format:

```toml
[task]
id_format = "jira"
default_status = "todo"
auto_detect_from_branch = true

[integrations.jira]
url = "https://company.atlassian.net"
username = "user@example.com"
default_project = "PROJ"

[integrations.github]
repository = "owner/repo"

[ai]
provider = "anthropic"
model = "claude-sonnet-4"
```

## Environment Variables

Configuration can also be set via environment variables:

```bash
# Override JIRA URL
export KNL_INTEGRATIONS_JIRA_URL="https://company.atlassian.net"

# Override AI API key (recommended for secrets)
export KNL_AI_API_KEY="your-api-key"
```

**Precedence:**
1. Environment variables (highest)
2. Local configuration
3. Global configuration (lowest)

## Next Steps

- [Configuration Guide](../configuration.md) - Configuration overview
- [Commands Reference](commands.md) - All commands
- [Installation](../installation.md) - Installation guide
