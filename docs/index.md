<div style="display: flex; justify-content: space-between; align-items: baseline;">
  <h1>KNL - Knowledge Retention Library</h1>
  <div style="font-size: 0.85em; color: #666; white-space: nowrap;">v1.2.0 | Updated: 2025-12-31</div>
</div>

A modern, AI-powered task management and development assistant that helps you retain context, maintain quality, and ensure consistency across your development work.

## What is KNL?

KNL (Knowledge Retention Library) is a command-line tool that:

- **Manages development tasks** with persistent context and memory
- **Enhances code quality** using AI-powered analysis (Claude)
- **Maintains development standards** across tasks
- **Generates tests** based on learned patterns
- **Assists with git workflows** (commits, PRs)
- **Transfers knowledge** between projects

Think of it as a development assistant that learns from your work and helps you stay productive.

## Key Features

### 🎯 Task Management
Track tasks linked to JIRA tickets or GitHub issues with rich context, auto-detection from branch names, and organized tests and documentation per task.

### 🤖 AI Integration
Powered by Claude Code via MCP (Model Context Protocol) for code quality analysis, test generation, consistent documentation, and smart commit messages.

### 📚 Knowledge Base
Local `.knowledge/` directory stores task history, learns and applies development standards, exports knowledge to new projects, with archive or reset options.

### 🍞 Knowledge Crumbs
Curated development knowledge deployed with KNL - bite-sized, actionable guides for DevOps, Testing, Security, and Development tasks. LLM-friendly format with YAML metadata.

### 🔧 Context Isolation
Strict separation between KNL and your project - KNL runs in its own virtual environment, never pollutes your dependencies, and works with any Python version.

## Quick Start

### Installation

=== "Repo-Local (Default)"

    Install KNL locally in your repository:

    ```bash
    cd your-repo
    curl -LsSf https://akaliazin.github.io/knl/install.sh | sh
    ```

    This creates `.knl/` in your repository with an isolated installation.

=== "User-Local"

    Install KNL globally for all projects:

    ```bash
    curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --user-local
    ```

    This installs to `~/.local/knl/` and adds to your PATH automatically.

=== "Compiled Binary"

    Maximum portability with minimal dependencies:

    ```bash
    curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled
    ```

    Requires only Python 3.8+ (vs 3.14+ for source). Perfect for CI/CD and distribution.

### Initialize in Your Repository

```bash
cd your-project
knl init
```

You'll be prompted to choose:

- Task ID format (JIRA or GitHub)
- Project identifier

### Create Your First Task

```bash
# JIRA-style
knl create PROJ-123

# GitHub-style
knl create "#456"

# With title
knl create PROJ-123 --title "Add user authentication"
```

## Why KNL?

### 🧠 Knowledge Retention
Unlike task trackers, KNL remembers and learns from each task to improve future work.

### 🎨 AI-Native
Built from the ground up with AI assistance in mind, designed to work seamlessly with Claude Code.

### 💻 Local-First
Your data stays on your machine. Optional cloud sync available.

### 👨‍💻 Developer-Focused
Built by developers, for developers. Adapts to your workflow, doesn't impose one.

### 🔌 Extensible
Easy to add custom scripts, templates, and workflows to match your team's needs.

## Next Steps

- [Installation Guide](installation.md) - Detailed installation instructions
- [Quick Start Guide](quickstart.md) - Get up and running quickly
- [Architecture](architecture/principles.md) - Understand KNL's design
- [CLI Reference](cli/commands.md) - Complete command documentation

## Support

- [GitHub Issues](https://github.com/akaliazin/knl/issues) - Report bugs or request features
- [GitHub Discussions](https://github.com/akaliazin/knl/discussions) - Ask questions and share ideas

## License

MIT License - see [LICENSE](https://github.com/akaliazin/knl/blob/main/LICENSE) file for details.
