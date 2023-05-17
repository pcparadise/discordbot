"""
An example module for future contributors to reference using events.
"""
import discord
from discord.ext import commands
import src.utils.errors as errors
import inspect

class CommandErrorHandler(commands.Cog):
    """
    An example class that inherits from commands.Cog for contributors to reference.
    This one uses events unlike the one in example_command_module
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        An event that triggers whenever a command encounters an error.

        This method recursively searches `src.utils.errors` for class names with defined messages
        and calls them if the corresponding error is raised.
        If the error does not match any defined error classes, a fallback error message is sent.
        """
        if isinstance(error, commands.CommandError):
            error_embed = discord.Embed()
            
            for class_name, obj in inspect.getmembers(errors):
                if inspect.isclass(obj) and hasattr(obj, 'message'):
                        error_message = getattr(obj, 'message')
                        if isinstance(error, getattr(errors, class_name)):
                            error_embed.add_field(name="Error", value=error_message)
                            break
            
            # Fallback error message
            if len(error_embed.fields) == 0:
                error_embed.add_field(name="Error", value="An error occurred while executing the command.")
            
            await ctx.send(embed=error_embed)
        else:
            await ctx.send("An error occurred.")
            return


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(CommandErrorHandler(bot))
