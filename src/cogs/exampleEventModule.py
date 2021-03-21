import asyncio
from discord.ext import commands
import discord

class exampleEventModule(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot 

    # Another decorator, and an async function called whenever
    # the discord bot is ready.
    # I reccomend looking into async/await and decorators to learn 
    # more.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'"{self.bot.user}" is ready.')


# This function is called by the load_extension method on the bot.
def setup(bot):
    bot.add_cog(exampleEventModule(bot))
