"""
The entry point for the discord bot. You can add modules by adding them
to the MODULES variable.
"""
import importlib
import sys

from discord.ext import commands

from .shared_state import SharedState


# add your module name here once completed
MODULES = ["help"]


def main():
    """
    The first function that runs.
    """
    try:
        config = SharedState("config.ini")
    except FileNotFoundError:
        print(
            "No config.ini was found\n"
            "valid config paths include the bot folder "
            "or the OS conventions your OS follows for configs "
            "(for example .config/ or $XDG_CONFIG_PATH on linux)",
            file=sys.stderr,
        )
        return
    bot = commands.Bot(command_prefix=config.prefix)
    bot.remove_command(
        "help"
    )  # removes the default help command, allowing for a replacement.

    print("Bot is starting...")
    load_modules(bot, config)
    bot.run(config.token)


def load_modules(bot, config):
    """
    Imports all modules in MODULES
    Passes through bot and config to the setup function.
    """
    for item in MODULES:
        importlib.import_module("cogs." + item).setup(bot, config)


if __name__ == "__main__":
    main()
