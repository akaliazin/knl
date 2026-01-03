"""Mock MCP server for documentation analysis.

This is a stub implementation that returns hardcoded responses to demonstrate
the documentation update workflow. In production, this would use Claude API
for real AI-powered analysis.
"""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool


def create_mock_proposal(task_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Create a mock documentation update proposal.

    In production, this would use Claude API to analyze the context and generate
    real proposals. For now, we return a hardcoded example.

    Args:
        task_id: Task ID being analyzed
        context: Context data from DocAnalyzer

    Returns:
        Mock DocUpdateProposal as dict
    """
    # Get actual counts from context
    commits_count = len(context.get("changes", {}).get("commits", []))
    files_count = len(context.get("changes", {}).get("files", []))

    return {
        "task_id": task_id,
        "scope": context.get("changes", {}).get("scope", "task"),
        "commits_analyzed": commits_count,
        "files_changed": files_count,
        "confidence": 0.85,
        "gaps": [
            {
                "gap_type": "missing_cli_documentation",
                "description": "README missing installation instructions for new --compiled flag",
                "severity": "high",
                "affected_files": ["README.md"],
                "code_reference": "install.sh:732",
                "suggested_action": "Add example showing --compiled flag usage in installation section",
            },
            {
                "gap_type": "missing_changelog",
                "description": "CHANGELOG missing entry for recent commits",
                "severity": "medium",
                "affected_files": ["CHANGELOG.md"],
                "code_reference": None,
                "suggested_action": "Add CHANGELOG entry summarizing recent documentation improvements",
            },
        ],
        "files": [
            {
                "path": "README.md",
                "file_type": "markdown",
                "section": "Installation",
                "updates": [
                    {
                        "type": "replace",
                        "old": "# Install latest version\ncurl -LsSf https://akaliazin.github.io/knl/install.sh | sh",
                        "new": "# Install latest version (source)\ncurl -LsSf https://akaliazin.github.io/knl/install.sh | sh\n\n# Install compiled binary (faster, fewer dependencies)\ncurl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled",
                        "reason": "Add example showing new --compiled installation flag",
                        "severity": "high",
                        "line_number": 50,
                    }
                ],
            },
            {
                "path": "CHANGELOG.md",
                "file_type": "markdown",
                "section": "Unreleased",
                "updates": [
                    {
                        "type": "insert",
                        "old": None,
                        "new": "## [Unreleased]\n\n### Added\n- MCP client for AI-powered documentation analysis\n- Documentation analyzer for context gathering\n- `knl docs update` command for AI-assisted doc updates\n- Interactive approval UI for reviewing documentation changes\n\n### Changed\n- Improved documentation coverage tracking\n- Enhanced CLI reference generation",
                        "reason": "Add CHANGELOG entry for recent documentation features",
                        "severity": "medium",
                        "line_number": 5,
                    }
                ],
            },
        ],
    }


async def main() -> None:
    """Run the MCP server."""
    server = Server("knl-docs-analyzer")

    # Register resources
    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available resources."""
        return [
            Resource(
                uri="knl://task/context",
                name="Task Context",
                mimeType="application/json",
                description="Current task context and metadata",
            ),
            Resource(
                uri="knl://changes",
                name="Code Changes",
                mimeType="application/json",
                description="Git commits and diffs",
            ),
            Resource(
                uri="knl://docs",
                name="Current Documentation",
                mimeType="application/json",
                description="Current documentation files",
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource - mock implementation."""
        # In production, this would fetch real data
        return json.dumps({"uri": uri, "mock": True})

    # Register tools
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="analyze_doc_gaps",
                description="Analyze code changes and identify documentation gaps",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to analyze"},
                        "context": {
                            "type": "object",
                            "description": "Documentation context from DocAnalyzer",
                        },
                    },
                    "required": ["task_id", "context"],
                },
            ),
            Tool(
                name="generate_doc_updates",
                description="Generate specific documentation update proposals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                        "context": {"type": "object", "description": "Analysis context"},
                        "gaps": {
                            "type": "array",
                            "description": "Identified documentation gaps",
                        },
                    },
                    "required": ["task_id", "context", "gaps"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls - mock implementation."""
        if name == "analyze_doc_gaps":
            # Mock analysis - in production, would use Claude API
            task_id = arguments.get("task_id", "unknown")
            context = arguments.get("context", {})

            # Generate mock proposal
            proposal = create_mock_proposal(task_id, context)

            return [TextContent(type="text", text=json.dumps(proposal, indent=2))]

        elif name == "generate_doc_updates":
            # Mock generation - in production, would use Claude API
            task_id = arguments.get("task_id", "unknown")
            context = arguments.get("context", {})

            # Generate mock proposal (same as analyze for this stub)
            proposal = create_mock_proposal(task_id, context)

            return [TextContent(type="text", text=json.dumps(proposal, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run() -> None:
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
