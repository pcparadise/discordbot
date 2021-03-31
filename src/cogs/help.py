"""
Mainly a help command that replaces the default command that discord.py provides.
This module also contains related commands and functions such as about, contrib, docs.
"""
import configparser

import discord
from discord.ext import commands


class Help(commands.Cog):
    """Defines everything related towards the help command."""

    def __init__(self, bot):
        self.embed_color = discord.Color.blurple()
        self.bot = bot
        self.config = configparser.ConfigParser()
        self.config.read("../config.ini")
        self.prefix = self.config.get("Bot", "Prefix")

    @commands.command(name="contrib", enabled=True)
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
        cog_dict = {}

        for cog in self.bot.cogs:
            cmd_dict = {}
            for cmd in self.bot.get_cog(cog).get_commands():
                cmd_item = {cmd.name: {"usage": cmd.usage, "doc_string": cmd.help}}
                cmd_dict.update(cmd_item)
            cog_dict[cog] = {
                "command_count": (len(self.bot.get_cog(cog).get_commands())),
                "commands": cmd_dict,
            }

        await ctx.send("```json\n{}```".format(cog_dict))

    # replaces the default help command
    @commands.command(name="help", aliases=["h"], usage=f"[command_name|cog_name]")
    async def send_help(self, ctx, *args):
        """Provides information about available commands."""

        argument = " ".join(args).lower().strip()

        cog_dict = {}
        lower_cog_list = []
        cmd_dict = {}
        lower_cmd_list = []
        uncategorized_cmd_dict = {}
        uncategorized_cmd_list_lower = []
        disabled_cmd_list = []

        for cog in self.bot.cogs:
            disabled_cog_cmd_list = []
            cmd_dict = {}
            for cmd in self.bot.get_cog(cog).get_commands():
                cmd_item = {
                    cmd.name: {
                        "name": cmd.name,
                        "usage": cmd.usage,
                        "doc_string": cmd.help,
                        "aliases": cmd.aliases,
                    }
                }
                cmd_dict[cmd.name] = {
                    "name": cmd.name,
                    "usage": cmd.usage,
                    "doc_string": cmd.help,
                    "aliases": cmd.aliases,
                }
                lower_cmd_list.append(cmd.name.lower())
                cmd_dict.update(cmd_item)
                if not cmd.enabled:
                    disabled_cmd_list.append(cmd.name)
                    disabled_cog_cmd_list.append(cmd.name)

            cog_dict[cog] = {
                "command_count": (
                    len(self.bot.get_cog(cog).get_commands())
                    - len(disabled_cog_cmd_list)
                ),
                "commands": cmd_dict,
            }
            lower_cog_list.append(cog.lower())

        for cmd in self.bot.walk_commands():
            if not cmd.name.lower() in lower_cmd_list:
                uncategorized_cmd_list_lower.append(cmd.name.lower())
                uncategorized_cmd_dict[cmd.name] = {
                    "name": cmd.name,
                    "usage": cmd.usage,
                    "doc_string": cmd.help,
                    "aliases": cmd.aliases,
                }

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
                embed.add_field(
                    name=cog,
                    value=f'`{cog_dict[cog]["command_count"]} commands`',
                    inline=True,
                )

            uncategorized_commands = ""
            for cmd in self.bot.walk_commands():
                if not cmd.name.lower() in lower_cmd_list:
                    uncategorized_commands += f"`{cmd.name}`, \n"

            if uncategorized_commands:
                embed.add_field(
                    name="Uncategorized Commands:",
                    value=uncategorized_commands[:-3],
                    inline=False,
                )

            await ctx.send(embed=embed)
        elif argument in lower_cog_list:
            parsable_json = cog_dict[list(cog_dict)[lower_cog_list.index(argument)]]

            description_string = ""
            for item in parsable_json["commands"]:
                doc_item = parsable_json["commands"][item]
                if doc_item["name"] in disabled_cmd_list:
                    pass
                else:
                    alias_string = ""
                    for alias in doc_item["aliases"]:
                        if alias:
                            alias_string += f"`{alias}`, "
                    alias_string = alias_string[:-2]
                    dash = ", " if alias_string else ""
                    usage = ""
                    if doc_item["usage"]:
                        usage = doc_item["usage"]
                    description_string += (
                        f"`{item}`{dash}{alias_string}:\n"
                        f'{doc_item["doc_string"]}\n'
                        f"```{self.prefix}{item} {usage}```\n\n"
                    )

            embed = discord.Embed(
                title=f"{argument.capitalize()} Module:",
                description=description_string,
                color=self.embed_color,
            )

            await ctx.send(embed=embed)
        elif argument in lower_cmd_list or argument in uncategorized_cmd_list_lower:
            if argument in lower_cmd_list:
                parsable_json = cmd_dict[list(cmd_dict)[lower_cmd_list.index(argument)]]
            elif argument in uncategorized_cmd_list_lower:
                parsable_json = uncategorized_cmd_dict[
                    list(uncategorized_cmd_dict)[
                        uncategorized_cmd_list_lower.index(argument)
                    ]
                ]

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
        else:
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