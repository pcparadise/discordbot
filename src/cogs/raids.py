"""
Modules for how PCParadise handles raids.
"""
import asyncio
import discord

from discord.ext import commands


class RaidHandler(commands.Cog):
    """
    Alert moderators of raids occuring and ban after asking moderators.
    """

    def __init__(self, bot, config):
        self.bot = bot
        # We use a set for their neat property of having an O(1) lookup time
        # they're unordered and unindexable though. But we don't need those properties.
        self.new_joins = set({})
        self.members_joined_during_raid = set({})
        mod_alert_channel_id = config.mod_alert_channel
        # NOTE: WE MUST ALWAYS AWAIT THIS VARIABLE.
        # WE CAN NOT HAVE AWAIT IN NON ASYNC METHODS, SO AWAIT THIS!
        self.alert_channel = bot.fetch_channel(mod_alert_channel_id)
        self.in_raid = False

    # I apologize for anyone reading this monstrosity.
    # Allow me to walk you through the thought process I guess.
    # We take a member when they join, and add them to a set called new_joins
    # We then remove them from said set after 5 seconds. This function can be run concurrently
    # whenever a new member joins - so it gradually fills up the new_joins set.
    # If the length exceeds 5 members - we send a message to the mods.
    # If the mods say it's okay,
    # ban all the members that joined during the raid. Otherwise, o well.
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Register new user and check if we're having a raid, using joins / time_period
        """
        self.new_joins.add(member)
        self.in_raid = False if len(self.new_joins) <= 5 else self.in_raid

        if len(self.new_joins) >= 5:
            if not self.in_raid:
                await self.alert_mods(
                    "A RAID HAS BEEN DETECTED. PLEASE RESPOND Y TO START BANNING"
                )
                alert_channel = await self.alert_channel
                msg = await self.bot.wait_for(
                    "message", lambda m: m.channel == alert_channel
                )
                self.in_raid = msg.content.lower().contains("y")
                if not self.in_raid:
                    # Apparently wasn't a raid, empty both sets.
                    self.members_joined_during_raid = set({})
                    self.new_joins = set({})

            for joined_member in self.new_joins:
                # we don't have to worry about duplicate members in
                # members_joined_during_raid because it's a set, not a list.
                self.members_joined_during_raid.add(joined_member)
                for raiding_member in self.members_joined_during_raid:
                    if self.in_raid:
                        try:
                            # await member.guild.ban(raiding_member)
                            print(
                                "Would of banned"
                                + raiding_member.name
                                + " "
                                + raiding_member.nick
                            )
                        except discord.Forbidden:
                            await self.alert_mods(
                                "Looks like I don't have the permission to ban!"
                            )
                        except discord.HTTPException:
                            # They've probably already been banned the previous run.
                            pass
                        self.members_joined_during_raid.remove(raiding_member)

        await asyncio.sleep(5)
        self.new_joins.remove(member.id)

        print(f'"{self.bot.user}" is ready.')

    async def alert_mods(self, msg):
        """
        Sends msg to mod alert channel
        """
        channel = await self.alert_channel
        await channel.send(msg)


# This function is called by the load_extension method on the bot.
def setup(bot, config):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    bot.add_cog(RaidHandler(bot, config))
