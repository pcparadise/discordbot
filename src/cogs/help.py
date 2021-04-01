"""
_﻿java﻿_"Mainly a help command that replaces the default command that discord.py provides.
This module also contains related commands and functions such as about, contrib, docs.
"""
import configparser
from contextlib import suppress

import discord
from discord.ext import commands


def find_ci(dictionary, string):
    """
    Returns a value for a key in a dictionary. Unlike normal indexing
    this is case insensitive, and returns None if no value exists
    """
    for key, value in dictionary.items():
        if key.lower() == string.lower():
            return value
    return None


def cog_values(bot):
    """Returns json for all cogs, commands and their related info."""
    disabled_cmds = []
    enabled_cmds = []
    cog_dict = {}
    misc_cmd_dict = {}
    all_cmds = {}

    for cog in bot.cogs:
        current_cog_disabled_cmds = []
        cmd_dict = {}

        for cmd in bot.get_cog(cog).get_commands():
            cmd_info = {
                "name": cmd.name,
                "usage": cmd.usage,
                "doc_string": cmd.help,
                "aliases": cmd.aliases,
            }
            cmd_item = {cmd.name: cmd_info}
            cmd_dict[cmd.name] = cmd_info
            all_cmds[cmd.name] = cmd_info

            cmd_dict.update(cmd_item)
            all_cmds.update(cmd_item)
            if not cmd.enabled:
                disabled_cmds.append(cmd.name)
                current_cog_disabled_cmds.append(cmd.name)
            else:
                enabled_cmds.append(cmd.name)

        cmd_count = len(bot.get_cog(cog).get_commands()) - len(
            current_cog_disabled_cmds
        )

        cog_dict[cog] = {
            "command_count": str(cmd_count),
            "commands": cmd_dict,
            "disabled_commands": current_cog_disabled_cmds,
        }

        cog_dict["disabled_commands"] = disabled_cmds
        cog_dict["enabled_commands"] = enabled_cmds

    for cmd in bot.walk_commands():
        if not cmd.name in cmd_dict.keys():
            misc_cmd_dict[cmd.name] = {
                "name": cmd.name,
                "usage": cmd.usage,
                "doc_string": cmd.help,
                "aliases": cmd.aliases,
            }

    misc_dicts = {"misc_commands": misc_cmd_dict, "all_commands": all_cmds}
    cog_dict.update(misc_dicts)

    return cog_dict


def misc_command_str(cog_dict):
    """Builds the uncategorized command string for the discord embed description."""
    uncategorized_commands = ""
    for cmd in cog_dict["misc_commands"]:
        uncategorized_commands += f"`{cmd}`, \n"
    return uncategorized_commands[:-3]


def description_string_builder(prefix, parsable_json, disabled_commands):
    """Builds the description command string for the discord embed description."""

    description_string = ""
    for item in parsable_json["commands"]:  # builds the embed description
        doc_item = parsable_json["commands"][item]
        if doc_item["name"] in disabled_commands:
            continue
        alias_string = ""
        for alias in doc_item["aliases"]:
            alias_string += f"`{alias}`, " if alias else None
        alias_string = alias_string[:-2]
        dash = ", " if alias_string else ""
        usage = doc_item["usage"] if doc_item["usage"] else None
        description_string += (
            f"`{item}`{dash}{alias_string}:\n"
            f'{doc_item["doc_string"]}\n'
            f"```{prefix}{item} {usage}```\n\n"
        )
    return description_string


class Help(commands.Cog):
    """Defines everything related towards the help command."""

    def __init__(self, bot):
        self.embed_color = discord.Color(0x2f3136)
        self.bot = bot
        self.config = configparser.ConfigParser()
        self.config.read("../config.ini")
        self.prefix = self.config.get("Bot", "Prefix")

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

    @commands.command(name="dump_help_json", enabled=False)
    async def dump_help_json(self, ctx):
        """Dumps all help data into a parsable json format. Useful for debugging."""
        cog_dict = cog_values(self.bot)
        await ctx.send("```json\n{}```".format(cog_dict))

    # replaces the default help command
    @commands.command(name="help", aliases=["h"], usage=f"[command_name|cog_name]")
    async def send_help(self, ctx, *args):
        """Provides information about available commands."""

        argument = " ".join(args).lower().strip()

        cog_dict = cog_values(self.bot)

        if not args:  # builds the embed if no arguments where provided
            embed = discord.Embed(
                title="Commands and modules",
                description=(
                    f"View a specific module or commands info with:\n"
                    f"```{self.prefix}help [module_name|command_name]```"
                ),
                color=self.embed_color,
            )

            for cog in cog_dict:
                with suppress(Exception):  # forced to use this because pylint
                    embed.add_field(
                        name=cog,
                        value=f'`{cog_dict[cog]["command_count"]} commands`',
                        inline=True,
                    )

            if cog_dict["misc_commands"]:
                embed.add_field(
                    name="Uncategorized Commands:",
                    value=misc_command_str(cog_dict),
                    inline=False,
                )

            await ctx.send(embed=embed)
            return

        find_ci_res = find_ci(cog_dict, argument)
        if find_ci_res:
            embed = discord.Embed(
                title=f"{argument.capitalize()} Module:",
                description=description_string_builder(
                    self.prefix, find_ci_res, cog_dict["disabled_commands"]
                ),
                color=self.embed_color,
            )

            await ctx.send(embed=embed)
            return

        arg_in_misc = find_ci(cog_dict["misc_commands"], argument)
        arg_in_dict = find_ci(cog_dict["all_commands"], argument)

        if arg_in_dict or arg_in_misc:

            parsable_json = arg_in_dict if arg_in_dict else arg_in_misc

            usage = "" if not parsable_json["usage"] else parsable_json["usage"]
            doc_string = (
                "undefined doc_string"
                if not parsable_json["doc_string"]
                else parsable_json["doc_string"]
            )

            embed = discord.Embed(
                title=f'{parsable_json["name"]} command:',
                description=(
                    f"{doc_string}\n"
                    f"**Example Usage:**\n"
                    f'```{self.prefix}{parsable_json["name"]} {usage}```'
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
def setup(bot):
    """Sets up the extension for the bot"""
    bot.add_cog(Help(bot))
