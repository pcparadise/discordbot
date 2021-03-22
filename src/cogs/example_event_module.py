"""
An example module for future contributors to reference using events.
"""

from discord.ext import commands

class ExampleEventModule(commands.Cog):
    """
    An example class that inherits from commands.Cog for contributors to reference.
    This one uses events unlike the one in example_command_module
    """
    def __init__(self, bot):
        self.bot = bot

    # Another decorator, and an async function called whenever
    # the discord bot is ready.
    # I reccomend looking into async/await and decorators to learn
    # more.
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints something when the bot is online.
        """
        print(f'"{self.bot.user}" is ready.')


# This function is called by the load_extension method on the bot.
def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    bot.add_cog(ExampleEventModule(bot))
