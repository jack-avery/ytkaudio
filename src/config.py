import configparser
import logging
import os
from platformdirs import user_config_dir

defaults = {
    "ytkaudio": {
        "outfolder": "",
        "mp3ify": True,
    }
}


def get_config_location() -> str:
    """
    Returns the configuration file location.
    """
    folder = user_config_dir("ytkaudio", "jack-avery", ensure_exists=True)
    return os.path.join(folder, "ytkaudio.cfg")


def load() -> configparser.ConfigParser:
    """
    Load the current configuration from `get_config_location()`.
    """
    location = get_config_location()
    logging.debug(f"loading config from {location}")

    config = configparser.ConfigParser()
    config.read_dict(defaults) # load defaults first
    config.read(location)
    return config


def save(config: configparser.ConfigParser) -> None:
    """
    Save `config` to `get_config_location()`.
    """
    location = get_config_location()
    logging.debug(f"saving config to {location}")

    with open(location, "w") as file:
        config.write(file, True)
