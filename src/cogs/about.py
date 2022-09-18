"""Module defining the cog \"About\""""
import discord
from discord.ext import commands
from src.main import PCParadiseBot


class About(commands.Cog):
    """Gives information about the bot"""

    def __init__(self, bot: PCParadiseBot):
        self.embed_color = discord.Color(0x2F3136)
        self.bot = bot
        self.prefix = self.bot.config.get("prefix")

    @commands.command(name="contrib")
    async def send_contribution_info(self, ctx):
        """Contains information about how to contribute to the bot."""

        contributing_md_url = (
            "https://github.com/pcparadise/discordbot/blob/main/CONTRIBUTING.md"
        )

        embed = discord.Embed(
            title="How To Contribute:",
            description=f"Visit: [{contributing_md_url[8:]}]({contributing_md_url})",
            color=self.embed_color,
        )

        await ctx.send(embed=embed)


async def setup(bot: PCParadiseBot):
    """Setup the About cog."""
    await bot.add_cog(About(bot))
