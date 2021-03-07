import asyncio
from discord.ext import commands
import discord

class exampleCommandModule(commands.Cog): # when this class is called, in a similar manner to a function, it runs the __init__ function, other functions can be created inside this class and called via exampleEventModule.FunctionName(), but init is always called first
    def __init__(self, bot):
        self.bot = bot # assigns the bot variable to a class variable

    @commands.command(name='ping', aliases=['pong', 'poong'])
    async def measure_ping(self, ctx):
        await ctx.send(f"Pong! 🏓 - {round(ctx.bot.latency *1000, 2)}ms") # sends a message if the name or any of the aliases is called

def setup(bot): # setup function that adds the module to the bot
    bot.add_cog(exampleCommandModule(bot))