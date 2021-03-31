"""
The entry point for the discord bot. You can add modules by adding them
to the MODULES variable.
"""
import configparser
from discord.ext import commands

CONFIG = configparser.ConfigParser()
CONFIG.read("../config.ini")

TOKEN = CONFIG.get("Discord", "Token")
PREFIX = CONFIG.get("Bot", "Prefix")

BOT = commands.Bot(command_prefix=PREFIX)
BOT.remove_command(
    "help"
)  # removes the default help command, allowing for a replacement.

# add your module name here once completed
MODULES = ["help"]


def main():
    """
    The first function that runs.
    """
    print("Bot is starting...")
    for module in MODULES:
        BOT.load_extension(f"cogs.{module}")
        print(f"cogs.{module} loaded")
    BOT.run(TOKEN)


main()
