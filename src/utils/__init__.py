"""
Utility functions for the entire discord bot
"""

import discord
from discord.ext.commands import Context

async def is_admin(ctx: Context) -> bool:
    """Returns true if the message author is an admin, replies and returns false if not."""
    match ctx.author:
        case discord.Member(guild_permissions=perms) if perms.administrator:
            return True
        case discord.Member(guild_permissions=perms) if not perms.administrator:
            await ctx.reply("You aren't an admin.")
        case _:
            pass
    return False
