"""
The entry point for the discord bot. You can add modules by adding them
to the MODULES variable.
"""
import importlib
import pathlib
import os
import appdirs

from discord.ext import commands
from shared_state import SharedState


def get_conf_path(filename):
    """
    Gets the config from a number of potential
    spots - either in tree or following the OS
    specific conventions and rules. On linux
    this would be the XDG specification for
    example. Returns None if no path was found.
    """
    # get the parent path of the parent path of the current file
    # this must be just above the "src/" directory
    program_path = pathlib.Path(__file__).absolute().parent.parent
    file_path = program_path / filename
    if os.path.exists(file_path):
        return str(file_path)

    # get where to store the file via the OS conventions. This is second in
    # priority from storing it directly with the program.
    os_conventioned_path = appdirs.user_config_dir("PCParadiseBot") + "/config.ini"
    if os.path.exists(os_conventioned_path):
        return os_conventioned_path

    # It wasn't found.
    return None


# add your module name here once completed
MODULES = ["help"]


def main():
    """
    The first function that runs.
    """
    conf_path = get_conf_path("config.ini")
    if not conf_path:
        print(
            "No config.ini was found\n"
            "valid config paths include the bot folder "
            "or the OS conventions your OS follows for configs "
            "(for example .config/ or $XDG_CONFIG_PATH on linux)"
        )
        return
    config = SharedState(conf_path)
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


main()
