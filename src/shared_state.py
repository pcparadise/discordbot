"""
Defines a class SharedState which acts as an
object to be passed around across modules which need
access to similar data such as the bot prefix
Takes in a config to initialize itself.
"""
import configparser


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


class SharedState:  # pylint: disable=too-few-public-methods
    """
    Creates a SharedState object
    SharedState contains information in variables that can be called from anywhere (cog/file).
    """

    def __init__(self, file_path):
        config = initialize_config(file_path)
        self.initialize_shared_state_variables(config)

    def initialize_shared_state_variables(self, config):
        """Initializes all variables within the SharedState object"""
        self.prefix = config["prefix"]
        self.token = config["token"]
