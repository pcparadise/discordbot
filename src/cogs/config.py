"""
A config module that updates values.
"""
from typing import List, Literal
import pytimeparse
import aiosqlite

import discord

from discord.abc import GuildChannel
from discord.ext import commands
from discord import app_commands, Role


class Config(commands.Cog):
    """
    A module that contains all the main configuration commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="disable_welcome_channel",
        description="Admin Only - Disables the welcome channel.",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def disable_welcome_channel(self, interaction: discord.Interaction):
        """Command that allows an admin to disable the welcome channel for a server."""
        assert interaction.guild
        server_id = interaction.guild.id

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
                await interaction.response.send_message(
                    (
                        "No welcome channel has been set up yet. "
                        "No action was taken. To set up a welcome channel, "
                        "run the command !enable_welcome_channel."
                    )
                )
                return

            await cur.execute(delete_server_settings, (server_id,))
            await database.commit()
            await interaction.response.send_message(
                (
                    "Success! To re-enable the "
                    "welcome channel run !enable_welcome_channel"
                )
            )

    @app_commands.command(
        name="enable_welcome_channel",
        description="Admin Only - Enables a welcome channel.",
    )
    @app_commands.describe(
        channel="The channel you would like to use as a welcome channel.",
        word="The word you want to use.",
        role="The role you want to assign.",
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_welcome_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role,
        word: str,
    ):
        """Enables a welcome channel where new users can verify \
        themselves by typing a certain word, and assigns \
        them a role based on their input."""

        assert interaction.guild

        server_id = interaction.guild.id

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
            res = await cur.execute(insert_sql, (server_id, word, role.id, channel.id))
            await database.commit()

            if res.rowcount >= 1:
                embed = discord.Embed(
                    title="Success!",
                    description=f"Channel: {channel.mention}\n"
                    f"Verification role: {role.mention}\n"
                    f"Verification word: `{word}`",
                )

                embed.add_field(
                    name="Role Permissions",
                    value=(
                        "```fix\nPlease configure role permissions according "
                        "to your desired functionality. For instance, you can restrict"
                        " channel access until users receive the appropriate role.```"
                    ),
                    inline=False,
                )

                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add_activity_rule")
    @app_commands.describe(
        channel="The channel you would like to use as a welcome channel.",
        role_for_rule="The role you want to assign.",
        message_count="The number of messages that must be sent.",
        timeout="Timespan of the rule",
        channels_for_rule="Either all, or a list of channels you wish to track.",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def add_rule(
        self,
        ctx: commands.Context,
        role_for_rule: Role,
        message_count: int,
        timeout: str,
        channels_for_rule: Literal["all"] | List[GuildChannel],
    ):  # pylint: disable=too-many-arguments
        """
        Adds a rule about activity tracking to the database for \
        assigning roles based off of channel activity.
        """
        assert ctx.guild

        time_period = pytimeparse.parse(timeout)
        if not time_period:
            await ctx.message.reply("Could not parse time period.")
            return None

        await ctx.message.reply("done!")
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
                (ctx.guild.id, int(time_period), role_for_rule.id, message_count),
            )

            id_fetch = await id_fetch.fetchone()
            assert id_fetch
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
            assert isinstance(channels_for_rule, GuildChannel)
            activity_tracking_channels = [
                (channel.id, activity_tracking_id) for channel in channels_for_rule
            ]
            await cur.executemany(
                insert_into_activity_tracking_channels, activity_tracking_channels
            )
            await database.commit()

    @commands.command(hidden=True)
    async def sync(self, ctx, guild_id=None):
        """
        Synchronizes the bot's slash commands with the Discord API.
        Arguments:
        - `guild_id` (optional): The ID of the guild to sync commands for. \
        If not provided, the bot will sync commands for all guilds.

        Usage:
        - `!sync`: Syncs all slash commands for all guilds the bot is a member of.
        - `!sync <guild_id>`: Syncs all slash commands for a specific guild.
        """
        sync_msg = await ctx.reply("Syncing commands...")

        if ctx.author.id not in self.bot.owners:
            raise commands.errors.NotOwner()

        guild_id = int(guild_id) if guild_id else None
        fmt = await self.bot.tree.sync()
        await sync_msg.edit(content=f"Synced `{len(fmt)}` command(s) globally.")


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(Config(bot))
