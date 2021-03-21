import asyncio
from discord.ext import commands
import discord

class exampleCommandModule(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot

    # Discord.py is an asynchronous discord framework. 
    # It makes heavy use of a python feature called "decorators."
    # I reccomend looking into both async/await and decorators to 
    # learn more abuot what's going on here.
    @commands.command(name='ping', aliases=['pong', 'poong'])
    async def measure_ping(self, ctx):
        await ctx.send(f"Pong! 🏓 - {round(ctx.bot.latency *1000, 2)}ms") 
 
# This function is called by the load_extension method on the bot.
def setup(bot):
    bot.add_cog(exampleCommandModule(bot))
