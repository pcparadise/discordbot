"""
An example module for future contributors to reference using events.
"""
import asyncio
import discord
from discord.ext import commands
import aiosqlite


class WelcomeModule(commands.Cog):
    """
    An example class that inherits from commands.Cog for contributors to reference.
    This one uses events unlike the one in example_command_module
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints something when the bot is online.
        """
        print(f'"{self.bot.user}" is ready.')

    @commands.Cog.listener()
    async def on_message(self, msg):
        """General on message discord event"""

        # sql logic to check if welcome channel is enabled in server and get config if so
        detection_word, role_id, welcome_channel_id = (
            None,
            None,
            None,
        )

        async with aiosqlite.connect(self.bot.db_path) as database:
            cur = await database.cursor()
            server_settings_query = (
                "SELECT detection_word, role_id, welcome_channel_id "
                "FROM welcome_config_settings "
                "WHERE server_id = ?"
            )
            await cur.execute(server_settings_query, (msg.guild.id,))
            result = await cur.fetchone()
            if result is None:
                return None
            detection_word, role_id, welcome_channel_id = result

        # a few checks to make pylint happy and just adds general logic
        is_detection_word = detection_word == msg.content.lower()
        is_welcome_channel = msg.channel.id == welcome_channel_id
        is_bypass = (
            msg.content.startswith("-") and msg.author.guild_permissions.administrator
        )

        if is_bypass:
            return None

        if (
            is_detection_word
            and not msg.author.bot
            and msg.guild
            and is_welcome_channel
        ):
            role = discord.utils.get(msg.guild.roles, id=role_id)
            await msg.author.add_roles(role, reason="Passed verification in #welcome")
            await msg.delete()

        elif not msg.author.bot and msg.guild and is_welcome_channel:
            embed = discord.Embed(
                title=f"Hey {msg.author.name}",
                description=(
                    "You have failed to verify yourself. "
                    "Please take the time to re-read the rules in order to "
                    "learn how to gain access to all channels on this server. "
                    "Thank you!"
                ),
            )

            failed_verify = await msg.channel.send(embed=embed)
            await msg.delete()

            await asyncio.sleep(10)
            await failed_verify.delete()


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(WelcomeModule(bot))
