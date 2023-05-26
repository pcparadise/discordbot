"""Module defining the cog \"About\""""
import discord
from discord import app_commands
from discord.ext import commands
from src.main import PCParadiseBot


class About(commands.Cog):
    """Gives information about the bot"""

    def __init__(self, bot: PCParadiseBot):
        self.bot = bot

    @app_commands.command(name="contrib")
    async def send_contribution_info(self, interaction: discord.Interaction):
        """Contains information about how to contribute to the bot."""

        contributing_md_url = (
            "https://github.com/pcparadise/discordbot/blob/main/CONTRIBUTING.md"
        )

        embed = discord.Embed(
            description=f"[How To Contribute]({contributing_md_url})",
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: PCParadiseBot):
    """Setup the About cog."""
    await bot.add_cog(About(bot))
