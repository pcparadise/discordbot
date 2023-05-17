"""
Contains custom error classes for command error handling in Discord bot commands.
Refer to CONTRIBUTING.md for more information
"""

from discord.ext import commands


class GuildCommandError(commands.CommandError):
    """Error raised when a command must be run inside a guild."""

    message = "This command must be run inside a guild."


class MemberCommandError(commands.CommandError):
    """Error raised when an invalid user is provided."""

    message = "Invalid user. Must be a member of the guild."


class BotCommandError(commands.CommandError):
    """Error raised when a bot user is provided."""

    message = "User cannot be a bot."
