"""
A module that provides error handling using events.
"""
import logging
import secrets

import discord
from discord.ext import commands


class CommandErrorHandler(commands.Cog):
    """A cog for handling command errors."""

    def __init__(self, bot):
        self.bot = bot

    logging.basicConfig(
        filename="error.log",
        filemode="a",
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.ERROR,
    )

    def generate_log_id(self):
        """Generates a unique ID with secrets.token_hex()"""
        return str(secrets.token_hex(4))

    def create_error_string(self, ctx, error):
        """Returns an error string depending on the error type."""
        # change to "/" when that's implemented
        prefix = "!"
        message = ""

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
                    f"seconds before using that command again."
                )
            case commands.NoPrivateMessage():
                message = "This command must be run inside of a guild."
            case commands.MemberNotFound():
                message = "Sorry, I couldn't find that member."
            case commands.MissingPermissions():
                message = (
                    "Hey! You don't have permissions to run that command! "
                    "What do you take me for? A fool??"
                )
            case commands.MissingRequiredArgument():
                message = (
                    "Seems like you're missing an argument.\n"
                    "Here's some more info:\n```fix\n"
                    f"{str(error) if str(error) else 'N/A'}```"
                    "_If that doesn't help, feel free to try_ "
                    f"`{prefix}help {ctx.message.content[1:]}`"
                )
            case commands.BadArgument():
                message = (
                    "Seems like one of the arguments you provided is "
                    "invalid.\nIf you need a refresher, feel free to check "
                    "the command usage with:\n```fix\n"
                    f"{prefix}help {ctx.command}```"
                )
            case commands.DisabledCommand():
                message = (
                    "Seems like someone disabled that command... I wonder "
                    "who that could be?"
                )
            case _:
                log_id = self.generate_log_id()
                error_classname = type(error).__name__
                logging.error("ID: %s | %s - %s", log_id, error_classname, str(error))

                message = (
                    "Oops, an error occurred while executing the command:\n"
                    f"```diff\n+ Error ID: {log_id}\n"
                    f"- {error_classname}{': ' + str(error) if str(error) else ''}```"
                    "Please try again, or contact bot support and "
                    f"provide the Error ID _({log_id})_."
                )
        return message

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """An event that triggers whenever a command encounters an error."""
        error_message = self.create_error_string(ctx, error)

        error_embed = discord.Embed()
        error_embed.add_field(name="Error", value=error_message)
        await ctx.send(embed=error_embed)


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(CommandErrorHandler(bot))
