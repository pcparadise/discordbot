"""
An example module for future contributors to reference using commands.
"""
from discord.ext import commands

class ExampleCommandModule(commands.Cog):
    """
    An example class that inherits from commands.Cog for contributors to reference.
    This one uses commands unlike the one in example_event_module
    """
    def __init__(self, bot):
        self.bot = bot

    # Discord.py is an asynchronous discord framework.
    # It makes heavy use of a python feature called "decorators."
    # I reccomend looking into both async/await and decorators to
    # learn more abuot what's going on here.
    @commands.command(name='ping', aliases=['pong', 'poong'])
    async def measure_ping(self, ctx):
        """
        Measures the bot latency to discord.
        """
        await ctx.send(f"Pong! 🏓 - {round(ctx.bot.latency *1000, 2)}ms")

# This function is called by the load_extension method on the bot.
def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    bot.add_cog(ExampleCommandModule(bot))
