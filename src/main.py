"""
The entry point for the discord bot. You can add cogs by adding them
to the EXTENSIONS variable.
"""
import asyncio
import configparser
import os
import pathlib
import sys
import traceback
from datetime import datetime
from typing import Union, Dict
import aiosqlite

# The type stubs for appdirs are fairly old.
# The mantainer seems open to accepting a PR
# but the original PR in 2019 seems to be inactive.
import appdirs  # type: ignore
import discord
from discord.ext import commands

import migrations

# List of cogs the bot will load on startup
# Names should follow the dot-path notation (similar to imports)
EXTENSIONS = [
    "src.cogs.help",
    "src.cogs.about",
    "src.cogs.logging",
    "src.cogs.activity_tracking",
    "src.cogs.welcome",
    "src.cogs.config",
    "src.cogs.error_handler",
]

# Define API Intents that we want to subscribe to
intents = discord.Intents.all()


class PCParadiseBot(commands.Bot):
    """
    Sub-class that inherits from commands.Bot to add additional attributes
    and have finer control over certain aspects of the bot.
    """

    def __init__(self):
        self.config = PCParadiseBot.initialize_config()

        db_path = PCParadiseBot.get_program_path() / "database.db"
        self.db_path = (
            pathlib.Path(self.config["databasepath"])
            if self.config.get("databasepath")
            else db_path
        )

        self.launch_time = datetime.utcnow()
        self.default_activity = discord.Activity(
            type=discord.ActivityType.listening, name=f"{self.config['prefix']}help"
        )

        self.prefix = self.config["prefix"]

        owner_ids = self.config["ownerid"].split(",")
        self.owners = [int(owner_id.strip()) for owner_id in owner_ids]

        # Call constructor of superclass Bot
        super().__init__(
            # Bot will respond to mention+cmd name and prefix+cmd name
            command_prefix=commands.when_mentioned_or(self.config["prefix"]),
            intents=intents,
            # Enables reconnect logic for when bot loses internet connection
            # or due to an issue communicating with the API
            reconnect=True,
        )

        asyncio.run(self.bot_startup())

    @staticmethod
    def get_program_path() -> pathlib.Path:
        """
        returns the path of the currently running program.
        """
        return pathlib.Path(__file__).absolute().parent.parent

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
        program_path = PCParadiseBot.get_program_path()
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
    def initialize_config() -> Dict[str, str]:
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

    async def bot_startup(self) -> None:
        """
        Blocking method that facilitates loading of all the
        bot's cogs along with any other preliminary setup.
        """
        print("Loading cogs...")
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
                print(f"SUCCESS - {extension}")
            except commands.ExtensionNotFound:
                print(f"FAILED - {extension}", file=sys.stderr)

    def run(self):  # pylint: disable=W0221
        """
        Overrides DPY's event loop initialization logic allowing for more fine control.
        """
        try:
            asyncio.run(migrations.run_migrations(self.db_path))
            asyncio.run(self.start(self.config["token"]))
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt Detected")
            asyncio.run(self.close())
            return
        except Exception:  # pylint: disable=W0703
            traceback.print_exc(file=sys.stderr)
            return

        # Perform a graceful shutdown
        asyncio.run(self.close())
        print("\nConnection Closed")

    async def on_ready(self):
        """
        Perform a few tasks when the bot is ready to accept commands.
        """
        # prove we have user id to the type system.
        assert self.user
        print(" - ")
        print("Client is ready")
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Discord.py Version - {discord.__version__}")
        print(f"Prefix - {self.config.get('prefix')}")
        print(" - ")

        print("The bot currently has access to the following guilds:")
        for guild in self.guilds:
            print(guild.name)

        async with aiosqlite.connect(self.db_path) as database:
            cur = await database.cursor()
            await cur.executemany(
                "INSERT OR IGNORE INTO servers VALUES (?)",
                [(guild.id,) for guild in self.guilds],
            )
            await database.commit()

        # Set the presence visible on the bot's profile
        await self.change_presence(
            status=discord.Status.online, activity=self.default_activity
        )

    @staticmethod
    async def on_disconnect():
        """
        Method that gets called whenever the client has disconnected from Discord
        or a connection attempt to Discord has failed.
        """
        print("\nClient has disconnected")


def main():
    """
    Entry point for poetry.
    """
    PCParadiseBot().run()


if __name__ == "__main__":
    main()
