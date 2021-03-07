import asyncio
from discord.ext import commands
import discord

class exampleEventModule(commands.Cog): # when this class is called, in a similar manner to a function, it runs the __init__ function, other functions can be created inside this class and called via exampleEventModule.FunctionName(), but init is always called first
    def __init__(self, bot):
        self.bot = bot # assigns the bot variable to a class variable

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'"{self.bot.user}" is ready.')


def setup(bot): # setup function that adds the module to the bot
    bot.add_cog(exampleEventModule(bot))