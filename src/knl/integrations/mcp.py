"""MCP (Model Context Protocol) client for AI-powered documentation analysis."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pydantic import BaseModel, Field


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


class MCPConnectionError(MCPError):
    """Failed to connect to MCP server."""

    pass


class MCPToolCallError(MCPError):
    """Error calling MCP tool."""

    pass


class MCPResourceError(MCPError):
    """Error accessing MCP resource."""

    pass


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""

    name: str = Field(description="Server name/identifier")
    command: str = Field(description="Command to start the server")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")


class MCPTool(BaseModel):
    """MCP tool definition."""

    name: str
    description: str | None = None
    input_schema: dict[str, Any] = Field(default_factory=dict)


class MCPResource(BaseModel):
    """MCP resource definition."""

    uri: str
    name: str
    mime_type: str | None = Field(None, alias="mimeType")
    description: str | None = None


class MCPClient:
    """
    Client for communicating with MCP servers.

    Supports calling tools and accessing resources on MCP servers.
    """

    def __init__(self, server_config: MCPServerConfig | str) -> None:
        """
        Initialize MCP client.

        Args:
            server_config: Server configuration or server name
        """
        if isinstance(server_config, str):
            # Look up server config by name
            self._server_name = server_config
            self._config = self._load_server_config(server_config)
        else:
            self._server_name = server_config.name
            self._config = server_config

        self._connected = False
        self._tools: dict[str, MCPTool] = {}
        self._resources: dict[str, MCPResource] = {}
        self._stdio_client: Any = None

    def _load_server_config(self, server_name: str) -> MCPServerConfig:
        """
        Load server configuration from KNL config.

        Args:
            server_name: Name of the server to load

        Returns:
            Server configuration

        Raises:
            MCPError: If server config not found
        """
        # Try to load from config
        # For now, use default config for knl-docs-analyzer
        if server_name == "knl-docs-analyzer":
            # Find KNL's venv Python (not the system Python)
            import sys
            from pathlib import Path

            # Get KNL installation directory from this file's location
            # This file is in src/knl/integrations/mcp.py
            # KNL venv should be at .knl/venv relative to the repo root
            knl_dir = Path(__file__).parent.parent.parent.parent / ".knl"
            if knl_dir.exists():
                venv_python = knl_dir / "venv" / "bin" / "python"
                if venv_python.exists():
                    python_cmd = str(venv_python)
                else:
                    python_cmd = sys.executable
            else:
                python_cmd = sys.executable

            return MCPServerConfig(
                name="knl-docs-analyzer",
                command=python_cmd,
                args=["-m", "knl_docs_analyzer.server"],
                env={},
            )
        msg = f"MCP server config not found: {server_name}"
        raise MCPError(msg)

    async def connect(self) -> None:
        """
        Connect to the MCP server.

        Raises:
            MCPConnectionError: If connection fails
        """
        if self._connected:
            return

        try:
            # Import MCP SDK (only when needed)
            try:
                from mcp import ClientSession, StdioServerParameters
                from mcp.client.stdio import stdio_client
            except ImportError as e:
                msg = (
                    "MCP SDK not installed. Install with: pip install 'knl[mcp]' or uv pip "
                    "install mcp"
                )
                raise MCPError(msg) from e

            # Create server parameters
            server_params = StdioServerParameters(
                command=self._config.command,
                args=self._config.args,
                env=self._config.env or None,
            )

            # Connect via stdio - stdio_client is an async context manager
            self._stdio_context = stdio_client(server_params)
            self._read_stream, self._write_stream = await self._stdio_context.__aenter__()

            # Create session
            self._session = ClientSession(self._read_stream, self._write_stream)

            # Initialize session
            await self._session.initialize()

            # List available tools and resources
            tools_result = await self._session.list_tools()
            self._tools = {tool.name: MCPTool(**tool.model_dump()) for tool in tools_result.tools}

            resources_result = await self._session.list_resources()
            self._resources = {
                resource.uri: MCPResource(**resource.model_dump())
                for resource in resources_result.resources
            }

            self._connected = True

        except ModuleNotFoundError as e:
            # MCP server module not installed
            if "knl_docs_analyzer" in str(e):
                msg = (
                    f"MCP server '{self._server_name}' is not installed.\n"
                    "This is optional - the docs update command will work with limited functionality.\n"
                    "To enable AI-powered analysis, install the MCP server:\n"
                    "  cd mcp-servers/knl-docs-analyzer && uv pip install -e ."
                )
            else:
                msg = f"Module not found while starting MCP server {self._server_name}: {e}"
            raise MCPConnectionError(msg) from e
        except Exception as e:
            msg = f"Failed to connect to MCP server {self._server_name}: {e}"
            raise MCPConnectionError(msg) from e

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if not self._connected:
            return

        try:
            # Exit the stdio context manager if it exists
            if hasattr(self, "_stdio_context"):
                await self._stdio_context.__aexit__(None, None, None)

            self._connected = False
            self._tools = {}
            self._resources = {}

        except Exception:
            # Best effort cleanup
            pass

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """
        Call a tool on the MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            MCPToolCallError: If tool call fails
            MCPConnectionError: If not connected
        """
        if not self._connected:
            msg = "Not connected to MCP server. Call connect() first."
            raise MCPConnectionError(msg)

        if name not in self._tools:
            available = ", ".join(self._tools.keys())
            msg = f"Tool '{name}' not found. Available tools: {available}"
            raise MCPToolCallError(msg)

        try:
            result = await self._session.call_tool(name, arguments=arguments or {})

            # Extract content from result
            if hasattr(result, "content") and result.content:
                # Get first content item
                content_item = result.content[0]
                if hasattr(content_item, "text"):
                    # Try to parse as JSON
                    try:
                        return json.loads(content_item.text)
                    except json.JSONDecodeError:
                        return content_item.text
                return str(content_item)

            return result

        except Exception as e:
            msg = f"Error calling tool '{name}': {e}"
            raise MCPToolCallError(msg) from e

    async def get_resource(self, uri: str) -> str:
        """
        Get a resource from the MCP server.

        Args:
            uri: Resource URI

        Returns:
            Resource content as string

        Raises:
            MCPResourceError: If resource access fails
            MCPConnectionError: If not connected
        """
        if not self._connected:
            msg = "Not connected to MCP server. Call connect() first."
            raise MCPConnectionError(msg)

        if uri not in self._resources:
            available = ", ".join(self._resources.keys())
            msg = f"Resource '{uri}' not found. Available resources: {available}"
            raise MCPResourceError(msg)

        try:
            result = await self._session.read_resource(uri)

            # Extract content from result
            if hasattr(result, "contents") and result.contents:
                content_item = result.contents[0]
                if hasattr(content_item, "text"):
                    return content_item.text
                if hasattr(content_item, "blob"):
                    return content_item.blob.decode("utf-8")
                return str(content_item)

            return str(result)

        except Exception as e:
            msg = f"Error reading resource '{uri}': {e}"
            raise MCPResourceError(msg) from e

    def list_tools(self) -> list[MCPTool]:
        """
        List available tools.

        Returns:
            List of available tools

        Raises:
            MCPConnectionError: If not connected
        """
        if not self._connected:
            msg = "Not connected to MCP server. Call connect() first."
            raise MCPConnectionError(msg)

        return list(self._tools.values())

    def list_resources(self) -> list[MCPResource]:
        """
        List available resources.

        Returns:
            List of available resources

        Raises:
            MCPConnectionError: If not connected
        """
        if not self._connected:
            msg = "Not connected to MCP server. Call connect() first."
            raise MCPConnectionError(msg)

        return list(self._resources.values())

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    async def __aenter__(self) -> MCPClient:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()


# Synchronous wrapper for convenience
def sync_call_tool(
    server: str | MCPServerConfig, tool_name: str, arguments: dict[str, Any] | None = None
) -> Any:
    """
    Synchronously call an MCP tool.

    Args:
        server: Server name or configuration
        tool_name: Tool to call
        arguments: Tool arguments

    Returns:
        Tool result
    """

    async def _call() -> Any:
        async with MCPClient(server) as client:
            return await client.call_tool(tool_name, arguments)

    return asyncio.run(_call())


def sync_get_resource(server: str | MCPServerConfig, uri: str) -> str:
    """
    Synchronously get an MCP resource.

    Args:
        server: Server name or configuration
        uri: Resource URI

    Returns:
        Resource content
    """

    async def _get() -> str:
        async with MCPClient(server) as client:
            return await client.get_resource(uri)

    return asyncio.run(_get())
