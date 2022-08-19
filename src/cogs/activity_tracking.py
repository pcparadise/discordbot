"""
A module to assign roles according to activity.
"""
from typing import List, Literal, Union
import pytimeparse
import aiosqlite
from discord import TextChannel
from discord.ext import commands
from discord.message import Message


class ActivityTracking(commands.Cog):
    """
    A module used to assign roles to users depending on how many
    messages they send in which channel. Run !add_rule
    in order to set this up.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_rule")
    async def add_rule(self, msg: Message):
        """
        Adds a rule about activity tracking to the database for assigning roles based off of channel
        activity.
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
            if not id_fetch:
                raise Exception("Failed to fetch when it should be impossible!")
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
def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    bot.add_cog(ActivityTracking(bot))
