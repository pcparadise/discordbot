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
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def disable_welcome_channel(self, msg: Message):
        """Command that allows an admin to disable the welcome channel for a server."""
        assert msg.guild
        server_id = msg.guild.id

        # deletes existing welcome settings
        async with aiosqlite.connect(self.bot.db_path) as database:
            cur = await database.cursor()

            select_server_settings = (
                "SELECT * FROM welcome_config_settings WHERE server_id = ?"
            )
            delete_server_settings = (
                "DELETE FROM welcome_config_settings WHERE server_id = ?"
            )

            await cur.execute(select_server_settings, (server_id,))
            result = await cur.fetchone()

            if not result:
                await msg.channel.send(
                    (
                        "No welcome channel has been set up yet. "
                        "No action was taken. To set up a welcome channel, "
                        "run the command !enable_welcome_channel."
                    )
                )
                return

            await cur.execute(delete_server_settings, (server_id,))
            await database.commit()
            await msg.channel.send(
                (
                    "Success! To re-enable the "
                    "welcome channel run !enable_welcome_channel"
                )
            )

    @commands.command(name="enable_welcome_channel")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_welcome_channel(self, msg: Message):
        """Enables a welcome channel where new users can verify \
        themselves by typing a certain word, and assigns \
        them a role based on their input."""
        assert msg.guild

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

    @commands.command(name="add_activity_rule")
    @commands.has_permissions(administrator=True)
    async def add_rule(self, msg: Message):
        """
        Adds a rule about activity tracking to the database for \
        assigning roles based off of channel activity.
        """
        if not msg.guild:
            await msg.reply(
                "Please run the command from a server you would like to apply this rule too!"
            )
            return

        await msg.reply(
            "What channel(s) would you like to apply this rule for? Type all for all."
        )

        def check(ctx):
            return ctx.author == msg.author and ctx.channel == msg.channel

        response = await self.bot.wait_for("message", check=check, timeout=30)
        channels_for_rule: Union[Literal["all"], List[TextChannel]]
        if response.content != "all":
            channels_for_rule = response.channel_mentions

            if not channels_for_rule:
                await response.reply("No channel mentions passed. Exiting")
                return
        else:
            channels_for_rule = "all"

        await response.reply("What role would you like to apply?")
        response: Message = await self.bot.wait_for("message", check=check, timeout=30)
        role_for_rule = (
            response.role_mentions[0]
            if response.role_mentions
            else msg.guild.get_role(int(response.content))
            if response.content.isnumeric()
            else None
        )

        if not role_for_rule:
            await response.reply("Invalid roles passed. Ending")
            return

        await response.reply("What time period should this rule check activity for?")
        response: Message = await self.bot.wait_for("message", check=check, timeout=30)

        time_period: int | float | None = pytimeparse.parse(response.content)
        if not time_period:
            await response.reply("Failed to parse time. Ending")
            return

        await response.reply("How many messages do they have to send?")
        response = await self.bot.wait_for("message", check=check, timeout=30)
        message_count = int(response.content) if response.content.isnumeric() else None
        if not message_count:
            await response.reply("Failed to parse message count. Ending")
            return

        await response.reply("done!")
        async with aiosqlite.connect(self.bot.db_path) as database:
            cur = await database.cursor()
            insert_settings_into = (
                "INSERT INTO activity_tracking_settings ("
                "server_id,"
                "time_period,"
                "role_id,"
                "message_count"
                ") VALUES (?, ?, ?, ?) RETURNING id;"
            )
            id_fetch = await cur.execute(
                insert_settings_into,
                (msg.guild.id, int(time_period), role_for_rule.id, message_count),
            )

            id_fetch = await id_fetch.fetchone()
            assert not id_fetch
            activity_tracking_id = id_fetch[0]

            insert_into_activity_tracking_channels = (
                "INSERT INTO activity_tracking_channels (channel, activity_tracking_id)"
                "VALUES (?, ?);"
            )

            # (fixme) Probably should represent this state in the database better, instead of
            # representing it as "absence of all channels" :')
            if channels_for_rule == "all":
                await database.commit()
                return
            activity_tracking_channels = [
                (channel.id, activity_tracking_id) for channel in channels_for_rule
            ]
            await cur.executemany(
                insert_into_activity_tracking_channels, activity_tracking_channels
            )
            await database.commit()


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(Config(bot))
