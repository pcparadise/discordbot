"""
An example module for future contributors to reference using commands.
"""
import discord
from discord.ext import commands
from discord import app_commands


class ExampleCommandModule(commands.Cog):
    """
    An example class that inherits from commands.Cog for contributors to reference.
    This one uses commands unlike the one in example_event_module
    """

    def __init__(self, bot):
        self.bot = bot

    # Discord.py is an asynchronous discord framework.
    # It makes heavy use of a python feature called "decorators."
    # I recommend looking into both async/await and decorators to
    # learn more about what's going on here.
    @app_commands.command(name="hello", description="Say hello!")
    @app_commands.describe(name="What's your name?")
    async def measure_ping(self, interaction: discord.Interaction, name: str):
        """Says hello to the user!"""
        await interaction.response.send_message(f"hi, {name}!")


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(ExampleCommandModule(bot))
