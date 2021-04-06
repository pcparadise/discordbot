"""
Mainly a help command that replaces the default command that discord.py provides.
This module also contains related commands and functions such as about, contrib, docs.
"""
from contextlib import suppress

import discord
from discord.ext import commands


def find(cond, iterator):
    """
    Returns the first value that matches f
    otherwise Returns None.
    """
    for i in iterator:
        if cond(i):
            return i
    return None


def misc_command_str(cmds):
    """Builds the uncategorized command string for the discord embed description."""
    uncategorized_commands = ""
    for cmd in cmds:
        uncategorized_commands += f"`{cmd.name}`, \n"
    return uncategorized_commands[:-3]


def description_string_builder(prefix, cog):
    """Builds the description command string for the discord embed description."""

    description_string = ""
    for cmd in cog.walk_commands():  # builds the embed description
        if not cmd.enabled:
            continue
        doc_item = cmd.description
        alias_string = ""
        for alias in cmd.aliases:
            alias_string += f"`{alias}`, " if alias else None
        alias_string = alias_string[:-2]
        dash = ", " if alias_string else ""
        usage = cmd.usage if cmd.usage else None
        description_string += (
            f"`{cmd.name}`{dash}{alias_string}:\n"
            f"{doc_item}\n"
            f"```{prefix}{cmd.name} {usage}```\n\n"
        )
    return description_string


class Information(commands.Cog):
    """Defines everything related towards the help command."""

    def __init__(self, bot, config):
        self.embed_color = discord.Color(0x2F3136)
        self.bot = bot
        self.config = config
        self.prefix = config.prefix

    @commands.command(name="contrib")
    async def send_contribution_info(self, ctx):
        """Contains information about how to contribute to the bot."""

        contributing_md_url = (
            "https://github.com/pcparadise/discordbot/blob/main/CONTRIBUTING.md"
        )

        embed = discord.Embed(
            title="How To Contribute:",
            description=f"Visit: [{contributing_md_url[8:]}]({contributing_md_url})",
            color=self.embed_color,
        )

        await ctx.send(embed=embed)

    # replaces the default help command
    @commands.command(name="help", aliases=["h"], usage="[command_name|cog_name]")
    async def send_help(self, ctx, *args):
        """Provides information about available commands."""

        argument = " ".join(args).lower().strip()

        if not args:  # builds the embed if no arguments where provided
            embed = discord.Embed(
                title="Commands and modules",
                description=(
                    f"View a specific module or commands info with:\n"
                    f"```{self.prefix}help [module_name|command_name]```"
                ),
                color=self.embed_color,
            )

            for cog in self.bot.cogs.values():
                enabled_cmds = [cmd for cmd in cog.walk_commands() if cmd.enabled]
                with suppress(Exception):  # forced to use this because pylint
                    embed.add_field(
                        name=cog.qualified_name,
                        value=f"`{len(enabled_cmds)} commands`",
                        inline=True,
                    )

            misc_commands = [cmd for cmd in self.bot.walk_commands() if cmd.cog is None]
            if misc_commands:
                embed.add_field(
                    name="Uncategorized Commands:",
                    value=misc_command_str(commands),
                    inline=False,
                )

            await ctx.send(embed=embed)
            return

        matching_cog = find(
            lambda cog: cog.qualified_name.lower() == argument.lower(),
            self.bot.cogs.values(),
        )
        if matching_cog:
            embed = discord.Embed(
                title=f"{argument.capitalize()} Module:",
                description=description_string_builder(self.prefix, matching_cog),
                color=self.embed_color,
            )

            await ctx.send(embed=embed)
            return

        matching_cmd = find(
            lambda cmd: cmd.name.lower() == argument.lower(),
            self.bot.walk_commands(),
        )

        if matching_cmd:
            doc_string = (
                "undefined doc_string" if not matching_cmd.help else matching_cmd.help
            )

            embed = discord.Embed(
                title=f"{matching_cmd.name} command:",
                description=(
                    f"{doc_string}\n"
                    f"**Example Usage:**\n"
                    f"```{self.prefix}{matching_cmd.name} {matching_cmd.usage if matching_cmd.usage else ''}```"
                ),
                color=self.embed_color,
            )

            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="404: Command or Module Not Found.",
            description=f"See: `{self.prefix}help`",
            color=self.embed_color,
        )

        await ctx.send(embed=embed)


# This function is called by the load_extension method on the bot.
def setup(bot, config):
    """Sets up the extension for the bot"""
    bot.add_cog(Information(bot, config))
