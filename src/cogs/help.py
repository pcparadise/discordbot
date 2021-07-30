"""
Mainly a help command that replaces the default command that discord.py provides.
This module also contains related commands and functions such as about, contrib, docs.
"""
from typing import Mapping, Optional
from collections.abc import Iterator
from functools import reduce

import discord
from discord.ext import commands
from fuzzywuzzy import fuzz


def count(iterable: Iterator) -> int:
    """count the amount of items in an iterator"""
    return sum(1 for i in iterable)


def command_usage(command: commands.Command) -> str:
    """Returns the command usage string for the command."""
    return f"!{command.name} {command.signature}"


class CustomHelp(commands.HelpCommand):
    """Help command for the bot.
    Defines how cogs, command groups, and commands are used."""

    @staticmethod
    def get_bot_help(
        mapping: Mapping[Optional[commands.Cog], list[commands.Command]]
    ) -> discord.Embed:
        """Generates the embed for the bot help command."""
        out = discord.Embed(title="Help")

        # this might be able to be cleaned up.
        freestanding_commands = []
        for cog, cmds in mapping.items():
            if cog is None:
                print(cmds)
                freestanding_commands.extend(cmds)
                continue
            out.add_field(
                name=cog.qualified_name,
                value=f"{count(cog.walk_commands())} commands.",
                inline=False,
            )

        if freestanding_commands != []:
            out.add_field(
                name="Freestanding Commands:",
                value="\n".join([cmd.name for cmd in freestanding_commands]),
                inline=False,
            )
        return out

    @staticmethod
    def get_cog_help(cog: commands.Cog) -> discord.Embed:
        """generates a help embed from the cog."""
        out = discord.Embed(title=cog.qualified_name, description=cog.description)
        for cmd_or_group in cog.walk_commands():
            # In python 3.10 this should be a match.
            if isinstance(cmd_or_group, commands.Group):
                out.add_field(
                    name=cmd_or_group.qualified_name,
                    value=f"{count(cmd_or_group.walk_commands())} commands.",
                )
                continue
            out.add_field(
                name=command_usage(cmd_or_group),
                value=cmd_or_group.help,
            )

        return out

    @staticmethod
    def get_command_help(cmd: commands.Command) -> discord.Embed:
        """generates a help embed from the cog."""
        out = discord.Embed(title=command_usage(cmd), description=cmd.help)
        return out

    def command_not_found(self, string: str) -> str:
        attempted_command = string.split()[0]
        mapping = self.get_bot_mapping()
        all_commands: list[list[commands.Command]] = [
            cmds for cog, cmds in mapping.items()
        ]

        def returning_extend(list1, list2):
            list1.extend(list2)
            return list1

        all_commands = reduce(returning_extend, all_commands, [])
        most_likely_commands = sorted(
            all_commands,
            key=lambda command: -fuzz.ratio(command.name, attempted_command),
        )
        new_line = "\n"
        return (
            f"{attempted_command} not found. Perhaps you meant one of the following:\n"
            f"{new_line.join([command.name for command in most_likely_commands[:3]])}"
        )

    async def send_command_help(self, command: commands.Command):
        """Sends the command help message"""
        dest = self.get_destination()
        await dest.send(embed=self.get_command_help(command))

    async def send_cog_help(self, cog: commands.Cog):
        """Sends the cog help message"""
        dest = self.get_destination()
        await dest.send(embed=self.get_cog_help(cog))

    async def send_bot_help(
        self, mapping: Mapping[Optional[commands.Cog], list[commands.Command]]
    ):
        """Sends the bot help message"""
        dest = self.get_destination()
        await dest.send(embed=self.get_bot_help(mapping))


# This function is called by the load_extension method on the bot.
def setup(bot):
    """Sets up the help command"""
    bot.help_command = CustomHelp()
