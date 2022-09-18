"""
A module to log events.
"""
import aiosqlite
from discord.ext import commands
from discord.message import Message


class Logging(commands.Cog):
    """
    A module that logs messages (without message content)
    from users if logging is active. Used for activity_tracking for e.g.
    role assignment.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        """
        Log every message when sent.
        """
        async with aiosqlite.connect(self.bot.db_path) as database:
            cur = await database.cursor()
            if not msg.channel or not msg.guild:
                return
            await cur.execute(
                "INSERT INTO message_log VALUES(?, ?, ?, ?)",
                (
                    msg.channel.id,
                    msg.author.id,
                    msg.created_at.timestamp(),
                    msg.guild.id,
                ),
            )
            await database.commit()


# This function is called by the load_extension method on the bot.
async def setup(bot):
    """
    Function called by load_extension method on the bot.
    This is used to setup a discord module.
    """
    await bot.add_cog(Logging(bot))
