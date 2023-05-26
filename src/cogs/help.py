"""
Mainly a help command that replaces the default command that discord.py provides.
This module also contains related commands and functions such as about, contrib, docs.
"""
from typing import Mapping, Optional, TypeVar, List
from collections.abc import Iterable

import difflib
import discord
from discord.ext import commands

from src.main import PCParadiseBot

# pylint: disable=invalid-name
T = TypeVar("T")
# pylint: enable=invalid-name


def codeblock(text: str) -> str:
    """Adds codeblock formatting to the given text."""
    return "```" + text + "```"


def flatten(nested_iterable: Iterable[Iterable[T]]) -> Iterable[T]:
    """Turns a set of listed iterables to an unested list of T."""
    return (item for iterable in nested_iterable for item in iterable)


def count(iterable: Iterable) -> int:
    """count the amount of items in an iterator."""
    return sum(1 for _ in iterable)


def command_usage(command: commands.Command) -> str:
    """Returns the command usage string for the command."""
    return f"!{command.name} {command.signature}"


class CustomHelp(commands.HelpCommand):
    """Help command for the bot.
    Defines how cogs, command groups, and commands are used."""

    @staticmethod
    def get_bot_help(
        mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
    ) -> discord.Embed:
        """Generates the embed for the bot help command."""
        out = discord.Embed(
            title="Help",
            description=(
                "To find out more info, use **!help [Cog/Command]**. "
                "Note that this is case sensitive."
            ),
        )

        freestanding_commands = []
        for cog, cmds in mapping.items():
            if cog is None:
                freestanding_commands.extend(cmds)
                continue
            visible_cmds = [cmd for cmd in cmds if not cmd.hidden]
            command_count = len(visible_cmds)
            if command_count != 0:
                command_logic = "command" if command_count == 1 else "commands"
                out.add_field(
                    name=cog.qualified_name,
                    value=codeblock(f"{command_count} {command_logic}"),
                    inline=True,
                )

        if freestanding_commands:
            visible_freestanding_commands = [
                cmd for cmd in freestanding_commands if not cmd.hidden
            ]
            if visible_freestanding_commands:
                out.add_field(
                    name="Freestanding Commands:",
                    value=codeblock(
                        "\n".join([cmd.name for cmd in visible_freestanding_commands])
                    ),
                    inline=False,
                )
        return out

    @staticmethod
    def get_cog_help(cog: commands.Cog) -> discord.Embed:
        """Generates a help embed from the cog."""
        out = discord.Embed(title=cog.qualified_name, description=cog.description)
        for cmd_or_group in cog.walk_commands():
            if cmd_or_group.hidden:
                continue  # Skip hidden commands

            if isinstance(cmd_or_group, commands.Group):
                out.add_field(
                    name=codeblock(cmd_or_group.qualified_name),
                    value=f"{count(cmd_or_group.walk_commands())} commands.",
                )
                continue

            out.add_field(
                name=command_usage(cmd_or_group),
                value=codeblock(
                    cmd_or_group.help if cmd_or_group.help else "No help given"
                ),
                inline=False,
            )

        return out

    @staticmethod
    def get_command_help(cmd: commands.Command) -> discord.Embed:
        """generates a help embed from the cog."""
        out = discord.Embed(title=command_usage(cmd), description=cmd.help)
        return out

    def command_not_found(self, string: str, /) -> discord.Embed:

        attempted_command = string.split()[0]
        # gets the input that discord.py passes to the default help command
        mapping = self.get_bot_mapping()
        # gets all commands from the default help and converts it to a string
        all_commands = [
            cmd.name for cmd in flatten(cmds for _, cmds in mapping.items())
        ]
        most_likely_command = difflib.get_close_matches(attempted_command, all_commands)

        out = discord.Embed(
            title=f"{attempted_command} not found",
            description="Note, everything is case sensitive",
        )

        if most_likely_command:
            out.add_field(
                name="Perhaps you meant:",
                value=codeblock(most_likely_command[0]),
            )

        return out

    async def send_error_message(self, error: str | discord.Embed, /):
        dest = self.get_destination()
        match error:
            case discord.Embed():
                await dest.send(embed=error)
            case _:
                await dest.send(error)

    async def send_command_help(self, command: commands.Command, /):
        """Sends the command help message"""
        dest = self.get_destination()
        await dest.send(embed=self.get_command_help(command))

    async def send_cog_help(self, cog: commands.Cog, /):
        """Sends the cog help message"""
        dest = self.get_destination()
        await dest.send(embed=self.get_cog_help(cog))

    async def send_bot_help(
        self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]], /
    ):
        """Sends the bot help message"""
        dest = self.get_destination()
        await dest.send(embed=self.get_bot_help(mapping))


# This function is called by the load_extension method on the bot.
async def setup(bot: PCParadiseBot):
    """Sets up the help command"""
    bot.help_command = CustomHelp()
