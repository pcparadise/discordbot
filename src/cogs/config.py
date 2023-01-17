"""
A config module that updates values.
"""
from typing import List, Literal, Union
import asyncio
import pytimeparse
import aiosqlite

import discord
from discord.ext import commands
from discord.message import Message
from discord import TextChannel
from src.utils import is_admin


class Config(commands.Cog):
    """
    A module that contains all the main configuration commands.
    """

    def __init__(self, bot):
        self.bot = bot

    async def prompt(self, ctx, prompt_message: str):
        """A basic function that prompts a user for a question"""
        await ctx.send(prompt_message)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            response = await self.bot.wait_for("message", check=check, timeout=30)
            return response.content
        except asyncio.TimeoutError:
            await ctx.send("Prompt timed out after 30 seconds. Setup cancelled.")
            return None

    @commands.command(name="disable_welcome_channel")
    @commands.check(is_admin)
    async def disable_welcome_channel(self, msg: Message):
        """Command that allows an admin to disable the welcome channel for a server."""
        server_id = msg.guild.id

        # deletes existing welcome settings
        try:
            async with aiosqlite.connect(self.bot.db_path) as database:
                cur = await database.cursor()

                select_server_settings = (
                    "SELECT * FROM welcome_config_settings WHERE server_id = ?"
                )
                delete_server_settings = (
                    "DELETE FROM welcome_config_settings WHERE server_id = ?"
                )

                result = await (
                    await cur.execute(select_server_settings, (server_id,))
                ).fetchone()

                if result:
                    await cur.execute(delete_server_settings, (server_id,))
                    await database.commit()
                    await msg.channel.send(
                        (
                            "Success! To re-enable the "
                            "welcome channel run !enable_welcome_channel"
                        )
                    )
        except aiosqlite.OperationalError as error:  # this is iffy
            if "no such column: server_id" in str(error):
                await msg.channel.send(
                    (
                        "No welcome channel has been set up yet. "
                        "No action was taken. To set up a welcome channel, "
                        "run the command !enable_welcome_channel."
                    )
                )

    @commands.command(name="enable_welcome_channel")
    @commands.check(is_admin)
    async def enable_welcome_channel(self, msg: Message):
        """Enables the welcome channel for a server.
        Prompts for data and updates sqlite table, you can also use this to update the info."""

        server_id = msg.guild.id

        def get_channel_id(guild: discord.Guild, channel: str) -> Union[int, None]:
            """
            Check if a channel is valid and return the channel ID if it is.
            """
            channel_id = None
            if channel.startswith("<#"):
                channel_id = int(channel.strip("<#>"))
            elif channel.startswith("#"):
                channel_name = channel.strip("#")
                channel_object = discord.utils.get(
                    guild.text_channels, name=channel_name
                )
                if channel_object:
                    channel_id = channel_object.id
            else:
                try:
                    channel_id = int(channel)
                except ValueError:
                    return None
            if discord.utils.get(guild.text_channels, id=channel_id) is not None:
                return channel_id
            return None

        channel_input = await self.prompt(
            msg, "What is the channel you would like to use as a welcome channel?"
        )
        if not channel_input:
            return
        channel_id = get_channel_id(msg.guild, channel_input)
        if channel_id is None:
            await msg.channel.send("Invalid channel ID or mention. Exiting.")
            return

        detection_word = await self.prompt(
            msg, "What is the detection word you want to use?"
        )
        if not detection_word:
            return None

        def get_role_id(guild: discord.Guild, role: str) -> Union[int, None]:
            """
            Check if a role is valid and return the role ID if it is.
            """
            role_id = None
            if role.startswith("<@&"):
                role_id = int(role.strip("<@&>"))
            else:
                try:
                    role_id = int(role)
                except ValueError:
                    return None
            if discord.utils.get(guild.roles, id=role_id) is not None:
                return role_id
            return None

        role_input = await self.prompt(
            msg,
            (
                "What is the _role_ you would like "
                f"to assign when a user says _{detection_word}_ in <#{channel_id}>?"
            ),
        )
        if not role_input:
            return
        role_id = get_role_id(msg.guild, role_input)
        if role_id is None:
            await msg.channel.send("Invalid Role ID or mention. Exiting.")
            return

        # updates the db with the new data
        async with aiosqlite.connect(self.bot.db_path) as database:
            cur = await database.cursor()

            insert_sql = (
                "INSERT INTO welcome_config_settings "
                "(server_id, detection_word, role_id, welcome_channel_id) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT (server_id) "
                "DO UPDATE SET detection_word = excluded.detection_word, "
                "role_id = excluded.role_id, welcome_channel_id = excluded.welcome_channel_id"
            )
            res = await cur.execute(
                insert_sql, (server_id, detection_word, role_id, channel_id)
            )
            await database.commit()
            if res.rowcount >= 1:
                await msg.channel.send(
                    f"Success! Welcome channel has been enabled in <#{channel_id}>. "
                    f"New users will now be able to verify by typing {detection_word}. "
                    f"Also make sure your _role permissions_ are setup to how you want, "
                    "this bot doesn't do that for you."
                )



# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(Config(bot))
