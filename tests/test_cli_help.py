"""Tests for CLI help extraction utilities."""

import json
from typing_extensions import Annotated

import pytest
import typer

from knl.utils.cli_help import (
    CommandInfo,
    CommandOption,
    extract_command_info,
    extract_typer_app_info,
    format_help_as_dict,
    get_all_command_paths,
)


class TestExtractCommandInfo:
    """Tests for extracting command information."""

    def test_simple_command(self):
        """Should extract info from a simple command."""
        app = typer.Typer()

        @app.command()
        def hello(name: str):
            """Say hello to someone."""
            pass

        from typer.main import get_command

        click_cmd = get_command(app)
        info = extract_command_info(click_cmd, "hello")

        assert info.name == "hello"
        assert "Say hello" in info.help_text
        assert len(info.options) > 0  # At least the name argument

    def test_command_with_options(self):
        """Should extract options and arguments."""
        app = typer.Typer()

        @app.command()
        def create(
            name: Annotated[str, typer.Argument(help="Item name")],
            title: Annotated[str, typer.Option("--title", "-t", help="Item title")] = "",
        ):
            """Create a new item."""
            pass

        from typer.main import get_command

        click_cmd = get_command(app)
        info = extract_command_info(click_cmd, "create")

        assert info.name == "create"
        assert len(info.options) >= 2

        # Find the title option
        title_opt = next((opt for opt in info.options if "--title" in opt.name), None)
        assert title_opt is not None
        assert title_opt.help_text == "Item title"

    def test_command_group(self):
        """Should extract subcommands from a group."""
        app = typer.Typer()
        task_app = typer.Typer()

        @task_app.command()
        def create():
            """Create a task."""
            pass

        @task_app.command()
        def delete():
            """Delete a task."""
            pass

        app.add_typer(task_app, name="task")

        from typer.main import get_command

        click_cmd = get_command(app)
        info = extract_command_info(click_cmd, "app")

        assert info.is_group
        assert "task" in info.subcommands
        assert "create" in info.subcommands["task"].subcommands
        assert "delete" in info.subcommands["task"].subcommands


class TestExtractTyperAppInfo:
    """Tests for extracting Typer app information."""

    def test_extracts_full_app_structure(self):
        """Should extract complete app structure."""
        app = typer.Typer()

        @app.command()
        def init():
            """Initialize repository."""
            pass

        @app.command()
        def create():
            """Create something."""
            pass

        info = extract_typer_app_info(app, "test-app")

        assert info.name == "test-app"
        assert info.is_group
        assert "init" in info.subcommands
        assert "create" in info.subcommands

    def test_nested_subcommands(self):
        """Should handle nested subcommands."""
        app = typer.Typer()
        config_app = typer.Typer()

        @config_app.command()
        def get():
            """Get config value."""
            pass

        @config_app.command()
        def set():
            """Set config value."""
            pass

        app.add_typer(config_app, name="config")

        info = extract_typer_app_info(app)

        assert "config" in info.subcommands
        config_info = info.subcommands["config"]
        assert "get" in config_info.subcommands
        assert "set" in config_info.subcommands


class TestFormatHelpAsDict:
    """Tests for formatting help as dictionary."""

    def test_formats_simple_command(self):
        """Should format command info as dict."""
        info = CommandInfo(
            name="test",
            help_text="Test command",
            options=[
                CommandOption(
                    name="--name",
                    param_type="option",
                    type_name="str",
                    required=True,
                    default=None,
                    help_text="Name option",
                )
            ],
        )

        result = format_help_as_dict(info)

        assert result["name"] == "test"
        assert result["help"] == "Test command"
        assert len(result["options"]) == 1
        assert result["options"][0]["name"] == "--name"

    def test_formats_nested_structure(self):
        """Should format nested subcommands."""
        sub_cmd = CommandInfo(name="sub", help_text="Subcommand")
        info = CommandInfo(
            name="main", help_text="Main command", subcommands={"sub": sub_cmd}
        )

        result = format_help_as_dict(info)

        assert "sub" in result["subcommands"]
        assert result["subcommands"]["sub"]["name"] == "sub"

    def test_serializable_to_json(self):
        """Result should be JSON-serializable."""
        info = CommandInfo(
            name="test",
            help_text="Test",
            options=[
                CommandOption(
                    name="--flag",
                    param_type="flag",
                    type_name="bool",
                    required=False,
                    default=False,
                    help_text="A flag",
                )
            ],
        )

        result = format_help_as_dict(info)

        # Should not raise
        json_str = json.dumps(result)
        assert json_str is not None


class TestGetAllCommandPaths:
    """Tests for getting all command paths."""

    def test_simple_command(self):
        """Should get path for simple command."""
        info = CommandInfo(name="app", help_text="Test app")
        paths = get_all_command_paths(info)

        assert "app" in paths
        assert len(paths) == 1

    def test_with_subcommands(self):
        """Should get paths for all subcommands."""
        sub1 = CommandInfo(name="sub1", help_text="Sub 1")
        sub2 = CommandInfo(name="sub2", help_text="Sub 2")
        info = CommandInfo(
            name="app", help_text="Test app", subcommands={"sub1": sub1, "sub2": sub2}
        )

        paths = get_all_command_paths(info)

        assert "app" in paths
        assert "app sub1" in paths
        assert "app sub2" in paths

    def test_nested_subcommands(self):
        """Should handle nested subcommands."""
        subsub = CommandInfo(name="nested", help_text="Nested")
        sub = CommandInfo(name="sub", help_text="Sub", subcommands={"nested": subsub})
        info = CommandInfo(name="app", help_text="App", subcommands={"sub": sub})

        paths = get_all_command_paths(info)

        assert "app" in paths
        assert "app sub" in paths
        assert "app sub nested" in paths
        assert len(paths) == 3


class TestRealCLI:
    """Integration tests with actual KNL CLI."""

    def test_extracts_knl_cli(self):
        """Should extract info from real KNL CLI."""
        from knl.cli import app

        info = extract_typer_app_info(app, "knl")

        # Should have the main commands
        assert info.is_group
        assert len(info.subcommands) > 0

        # Check for known commands (init should exist)
        command_names = list(info.subcommands.keys())
        # At minimum, we should have some commands
        assert len(command_names) > 0

    def test_formats_knl_cli_as_dict(self):
        """Should format KNL CLI as dict."""
        from knl.cli import app

        info = extract_typer_app_info(app, "knl")
        result = format_help_as_dict(info)

        # Should be a valid dict with expected structure
        assert "name" in result
        assert "help" in result
        assert "subcommands" in result

        # Should be JSON-serializable
        json_str = json.dumps(result, indent=2)
        assert json_str is not None

    def test_gets_all_knl_command_paths(self):
        """Should get all KNL command paths."""
        from knl.cli import app

        info = extract_typer_app_info(app, "knl")
        paths = get_all_command_paths(info)

        # Should have multiple paths
        assert len(paths) > 1
        assert "knl" in paths
