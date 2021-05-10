"""
The entry point for the discord bot. You can add cogs by adding them
to the EXTENSIONS variable.
"""
import configparser
import os
import pathlib
import sys
import traceback
from datetime import datetime
from typing import Union

import appdirs
import discord
from discord.ext import commands


# List of cogs the bot will load on startup
# Names should follow the dot-path notation (similar to imports)
EXTENSIONS = ["cogs.help"]


# Define API Intents that we want to subscribe to
intents = discord.Intents.all()


class PCParadiseBot(commands.Bot):
    """
    Sub-class that inherits from commands.Bot to add additional attributes
    and have finer control over certain aspects of the bot.
    """

    def __init__(self):
        self.config = PCParadiseBot.initialize_config()
        self.launch_time = datetime.utcnow()
        self.default_activity = discord.Activity(
            type=discord.ActivityType.listening, name=f"{self.config.get('prefix')}help"
        )

        # Call constructor of superclass Bot
        super().__init__(
            # Bot will respond to mention+cmd name and prefix+cmd name
            command_prefix=commands.when_mentioned_or(self.config.get("prefix")),
            # Removes the default help command, in the future we can
            # pass our HelpCommand sub-class to the constructor
            help_command=None,
            intents=intents,
            # Enables reconnect logic for when bot loses internet connection
            # or due to an issue communicating with the API
            reconnect=True,
        )

        self.bot_startup()

    @staticmethod
    def get_conf_path(file_name: str) -> Union[str, None]:
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
        file_path = program_path / file_name
        if os.path.exists(file_path):
            return str(file_path)

        # get where to store the file via the OS conventions. This is second in
        # priority from storing it directly with the program.
        os_conventioned_path = (
            appdirs.user_config_dir("PCParadiseBot") + f"/{file_name}"
        )
        if os.path.exists(os_conventioned_path):
            return os_conventioned_path

        # We couldn't find the config file
        return None

    @staticmethod
    def initialize_config() -> dict:
        """
        Loads the config, parses it, ignores sections, and returns it as a dictionary.
        """
        # Get the filepath of our config file
        file_name = "config.ini"
        file_path = PCParadiseBot.get_conf_path(file_name)

        # Prevent bot from continuing further execution if the config file could not be found
        if not file_path:
            sys.exit(
                f"No file named {file_name} was found.\n"
                "Valid config paths include the bot folder "
                "or the conventions your OS follows for configs "
                "(for example .config/ or $XDG_CONFIG_PATH on linux)."
            )

        # Initialize ConfigParser object
        temp_config = configparser.ConfigParser()
        temp_config.read(file_path)

        # Populate a dictionary with the fields from our config file
        config = {}
        for section in temp_config.sections():
            for key, val in temp_config.items(section):
                config[key] = val

        return config

    def bot_startup(self):
        """
        Blocking method that facilitates loading of all the
        bot's cogs along with any other preliminary setup.
        """
        print("Loading cogs...")
        for extension in EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f"SUCCESS - {extension}")
            except commands.ExtensionNotFound:
                print(f"FAILED - {extension}", file=sys.stderr)

    def run(self):  # pylint: disable=W0221
        """
        Overrides DPY's event loop initialization logic allowing for more fine control.
        """
        try:
            self.loop.run_until_complete(self.start(self.config.get("token")))
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt Detected")
            self.loop.run_until_complete(self.close())
            return
        except Exception:  # pylint: disable=W0703
            traceback.print_exc(file=sys.stderr)
            return

        # Perform a graceful shutdown
        self.loop.run_until_complete(self.close())
        print("\nConnection Closed")

    async def on_ready(self):
        """
        Perform a few tasks when the bot is ready to accept commands.
        """
        print(" - ")
        print("Client is ready")
        print(
            f"Logged in as {self.user.name}#{self.user.discriminator} (ID: {self.user.id})"
        )
        print(f"Discord.py Version - {discord.__version__}")
        print(f"Prefix - {self.config.get('prefix')}")
        print(" - ")

        print("The bot currently has access to the following guilds:")
        for guild in self.guilds:
            print(guild.name)

        # Set the presence visible on the bot's profile
        await self.change_presence(
            status=discord.Status.online, activity=self.default_activity
        )

    async def on_disconnect(self):
        """
        Method that gets called whenever the client has disconnected from Discord
        or a connection attempt to Discord has failed.
        """
        print("\nClient has disconnected")



if __name__ == "__main__":
    PCParadiseBot().run()