"""
A module to assign roles according to activity.
"""
from asyncio import sleep
from typing import Iterable, List, Optional, Tuple
import aiosqlite
from discord import Guild
from discord import errors
from discord.ext import commands


class ActivityTracking(commands.Cog):
    """
    A module used to assign roles to users depending on how many
    messages they send in which channel. Run !add_rule
    in order to set this up.
    """

    def __init__(self, bot):
        self.bot = bot

    async def check_for_role_grant(self) -> List[Tuple[int, int, int]]:
        """
        Checks who should be granted roles.
        Returns: a list of tuple[int, int, int]. First value is
        role id that should be assigned, second is user id, and third
        is server id.
        """
        async with aiosqlite.connect(self.bot.db_path) as database:
            cur = await database.cursor()
            cur = await cur.execute(
                "SELECT role_id, user_id, a.server_id FROM activity_tracking_settings a\n"
                "  INNER JOIN message_log m, activity_tracking_channels c\n"
                "ON\n"
                "  c.activity_tracking_id = id AND\n"
                "  m.channel_id = c.channel\n"
                "GROUP BY a.id\n"
                "HAVING\n"
                '  COUNT(time_period > strftime("%s") - `time`) >= message_count\n'
            )
            return list(map(tuple, await cur.fetchall()))

    async def assign_roles(self, info: Iterable[Tuple[int, int, int]]) -> None:
        """
        Takes a iterator of (role_id, user_id, server_id), and assigns roles to the user.
        """
        for role_id, user_id, server_id in info:
            guild: Optional[Guild] = self.bot.get_guild(server_id)
            if not guild:
                continue
            member = guild.get_member(user_id)
            if not member:
                continue
            role = guild.get_role(role_id)
            if not role:
                continue
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        setup collection event which configures all this.
        """
        cache = set(await self.check_for_role_grant())
        while True:
            await sleep(5)
            # There's a race condition here where the first sent message
            # before the bot is fully up already got logged, and hence is a part of the cache. :)
            new_results = set(await self.check_for_role_grant())
            need_to_set = new_results.difference(cache)
            try:
                await self.assign_roles(need_to_set)
            # we need a better way to handle this so we don't keep retrying constantly
            # but instead put it on a /far/ higher cooldown. Perhaps we can do the same
            # for invalidating the cache?
            except errors.Forbidden:
                print("Need to set up a cog for logging to alert channel eventually")
                continue
            cache = new_results


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(ActivityTracking(bot))
