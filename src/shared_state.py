"""
Defines a class SharedState which acts as an
object to be passed around across modules which need
access to similar data such as the bot prefix.
Takes in a config file name to initialize itself.
"""

import configparser
import os
import pathlib

import appdirs


def initialize_config(file_path):
    """
    Loads the config, parses it, ignores sections, and returns it as a dictionary
    """
    temp_config = configparser.ConfigParser()
    temp_config.read(file_path)

    config = {}
    for section in temp_config.sections():
        for key, val in temp_config.items(section):
            config[key] = val

    return config


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


class SharedState:  # pylint: disable=too-few-public-methods
    """
    Creates a SharedState object
    SharedState contains information in variables that can be called from anywhere (cog/file).
    """

    def __init__(self, filename):
        file_path = get_conf_path(filename)
        if not file_path:
            raise FileNotFoundError
        config = initialize_config(file_path)
        self.initialize_shared_state_variables(config)

    def initialize_shared_state_variables(self, config):
        """Initializes all variables within the SharedState object"""
        self.prefix = config["prefix"]
        self.token = config["token"]
        self.mod_alert_channel = config["mod_alert_channel"]
