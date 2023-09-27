"""
A module that provides error handling using events.
"""
import logging
import secrets
import sys

import discord
from discord.ext import commands


class CommandErrorHandler(commands.Cog):
    """A cog for handling traditional command errors."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """An event that triggers whenever a command encounters an error."""
        if ctx.message.content.startswith("!!"):
            return None

        match create_error_string(error):
            case (message, footer):
                await ctx.send(embed=build_error_embed(message, footer))
                return
        message, footer = log_unexpected_error(error)
        await ctx.send(embed=build_error_embed(message, footer))


def log_unexpected_error(error):
    """
    This logs an unexpected error, and returns a message, footer tuple
    to show the user.
    """
    log_id = generate_log_id()
    error_classname = type(error).__name__
    logging.error("ID: %s | %s - %s", log_id, error_classname, str(error))

    print(error, file=sys.stderr)
    message = (
        "Oops, an error occurred while executing the command:\n"
        f"```diff\n+ Error ID: {log_id}\n"
        f"- {error_classname}{': ' + str(error) if str(error) else ''}```"
    )
    footer = (
        "Please try again, or contact bot support and "
        f"provide the Error ID ({log_id})."
    )
    return message, footer


def generate_log_id():
    """Generates a unique ID with secrets.token_hex()"""
    return str(secrets.token_hex(4))


def build_error_embed(message, footer):
    """
    Builds an embed using a message and footer to show the user.
    """
    error_embed = discord.Embed()
    error_embed.add_field(name="Error", value=message)
    if footer:
        error_embed.set_footer(text=footer)

    return error_embed


def create_error_string(error):
    """Returns a message and footer to show the user depending on the error type."""

    # change to "/" when that's implemented
    message, footer = "", ""

    match error:
        # to utilize this, create a custom class that inherits from commands.CommandError
        # and define message as a string
        case commands.CommandError(message=message) if message is not None:
            return message
        case commands.CommandNotFound():
            message = "Sorry, I don't have that command... _(yet)_."
        case commands.CommandOnCooldown():
            message = (
                f"Please wait **{round(error.retry_after, 1)}** "
                "seconds before using that command again."
            )
        case commands.NoPrivateMessage():
            message = "This command must be run inside of a guild."
        case commands.MemberNotFound():
            message = f"Sorry, I couldn't find the member `@{error.argument}`."
        case commands.MissingPermissions():
            message = (
                "Hey! You don't have permissions to run that command! "
                "What do you take me for? A fool??"
            )
        case commands.BotMissingPermissions():
            missing_permissions = ", ".join(error.missing_permissions)
            message = (
                "Sorry, I don't have permissions to do that.\n"
                "I'm missing the following permission(s):"
                f"```fix\n{missing_permissions}```"
            )
        case commands.MissingRequiredArgument():
            message = (
                "Missing argument:\n```fix\n"
                f"{str(error.param) if str(error.param) else 'N/A'}```"
            )
        case commands.BadArgument():
            message = "Got an invalid argument. Check the arguments again."
        case commands.DisabledCommand():
            message = (
                "Seems like someone disabled that command... I wonder "
                "who that could be?"
            )
        case _:
            # we don't have a handler for this error
            return None
    return message, footer


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(CommandErrorHandler(bot))

    logging.basicConfig(  # configure log file.
        filename="error.log",
        filemode="a",
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.ERROR,
    )

    @bot.tree.error
    async def on_app_command_error(
        interaction: discord.Interaction, error: discord.app_commands.AppCommandError
    ) -> None:
        match create_error_string(error.original):
            case (message, footer):
                await interaction.response.send_message(
                    embed=build_error_embed(message, footer)
                )
                return
        message, footer = log_unexpected_error(error)
        await interaction.response.send_message(
            embed=build_error_embed(message, footer)
        )
