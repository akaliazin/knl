"""CLI help text extraction utilities for documentation automation."""

import inspect
from dataclasses import dataclass, field
from typing import Any

import typer
from typer.core import TyperCommand, TyperGroup


@dataclass
class CommandOption:
    """Represents a CLI command option/argument."""

    name: str
    """Option name (e.g., '--title', '-t')"""

    param_type: str
    """Parameter type (option, argument, flag)"""

    type_name: str
    """Type annotation (str, int, bool, etc.)"""

    required: bool
    """Whether the parameter is required"""

    default: Any
    """Default value if not required"""

    help_text: str
    """Help text description"""

    metavar: str | None = None
    """Metavar for display in help"""


@dataclass
class CommandInfo:
    """Represents a CLI command with its help information."""

    name: str
    """Command name"""

    help_text: str
    """Command help/docstring"""

    options: list[CommandOption] = field(default_factory=list)
    """List of command options/arguments"""

    subcommands: dict[str, "CommandInfo"] = field(default_factory=dict)
    """Nested subcommands if this is a group"""

    is_group: bool = False
    """Whether this command has subcommands"""


def extract_option_info(param: Any) -> CommandOption:
    """
    Extract information from a Click/Typer parameter.

    Args:
        param: Click Parameter object

    Returns:
        CommandOption with extracted information
    """
    # Determine parameter type
    if isinstance(param, typer.core.TyperArgument):
        param_type = "argument"
    elif param.is_flag:
        param_type = "flag"
    else:
        param_type = "option"

    # Get type name
    type_name = "str"
    if hasattr(param, "type"):
        if hasattr(param.type, "name"):
            type_name = param.type.name
        else:
            type_name = str(param.type)

    # Get option names (e.g., ['--title', '-t'])
    names = param.opts or param.secondary_opts or []
    name = names[0] if names else param.name or ""

    return CommandOption(
        name=name,
        param_type=param_type,
        type_name=type_name,
        required=param.required,
        default=param.default,
        help_text=param.help or "",
        metavar=param.metavar,
    )


def extract_command_info(
    command: TyperCommand | TyperGroup, command_name: str = ""
) -> CommandInfo:
    """
    Extract help information from a Typer command.

    Args:
        command: Typer command or group
        command_name: Name of the command

    Returns:
        CommandInfo with extracted help information
    """
    # Get command help text
    help_text = command.help or ""
    if command.callback and command.callback.__doc__:
        help_text = command.callback.__doc__.strip()

    # Check if this is a command group
    is_group = isinstance(command, TyperGroup)

    # Extract options/arguments
    options = []
    if hasattr(command, "params"):
        for param in command.params:
            options.append(extract_option_info(param))

    # Extract subcommands if this is a group
    subcommands = {}
    if is_group and hasattr(command, "commands"):
        for sub_name, sub_cmd in command.commands.items():
            subcommands[sub_name] = extract_command_info(sub_cmd, sub_name)

    return CommandInfo(
        name=command_name or command.name or "",
        help_text=help_text,
        options=options,
        subcommands=subcommands,
        is_group=is_group,
    )


def extract_typer_app_info(app: typer.Typer, app_name: str = "knl") -> CommandInfo:
    """
    Extract complete help information from a Typer app.

    Args:
        app: Typer application
        app_name: Name of the application

    Returns:
        CommandInfo representing the entire CLI structure
    """
    # Get the Click group from Typer app
    # We need to call typer.main.get_command() to get the Click command
    from typer.main import get_command

    click_command = get_command(app)

    return extract_command_info(click_command, app_name)


def format_help_as_dict(info: CommandInfo) -> dict[str, Any]:
    """
    Format CommandInfo as a dictionary for serialization.

    Args:
        info: CommandInfo to format

    Returns:
        Dictionary representation
    """
    return {
        "name": info.name,
        "help": info.help_text,
        "is_group": info.is_group,
        "options": [
            {
                "name": opt.name,
                "type": opt.param_type,
                "value_type": opt.type_name,
                "required": opt.required,
                "default": str(opt.default) if opt.default is not None else None,
                "help": opt.help_text,
            }
            for opt in info.options
        ],
        "subcommands": {
            name: format_help_as_dict(subcmd)
            for name, subcmd in info.subcommands.items()
        },
    }


def get_all_command_paths(info: CommandInfo, prefix: str = "") -> list[str]:
    """
    Get list of all command paths in the CLI.

    Args:
        info: CommandInfo to traverse
        prefix: Current command path prefix

    Returns:
        List of command paths (e.g., ['knl', 'knl create', 'knl task update'])
    """
    paths = []

    # Add current command
    current_path = f"{prefix} {info.name}".strip()
    paths.append(current_path)

    # Add subcommands recursively
    for subcmd in info.subcommands.values():
        paths.extend(get_all_command_paths(subcmd, current_path))

    return paths
