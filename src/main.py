"""
The entry point for the discord bot. You can add modules by adding them
to the MODULES variable.
"""
import importlib
from discord.ext import commands
from shared_state import SharedState

CONFIG = SharedState("../config.ini")

BOT = commands.Bot(command_prefix=CONFIG.prefix)
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
    load_modules()
    BOT.run(CONFIG.token)


def load_modules():
    """
    Imports all modules in a given list.
    Passes through bot and config to the setup function.
    """
    for item in MODULES:
        importlib.import_module("cogs." + item).setup(BOT, CONFIG)


main()
