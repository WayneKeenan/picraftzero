import logging
import json
from configparser import ConfigParser
from os.path import expanduser, join, split
from .log import logger


CONFIG_FILE="picraftzero.cfg"

# order of precedence is low to high:
CONFIG_CANDIDATES = [
                join(join(split(__file__)[0],'resources/config', CONFIG_FILE)),      # built-in defaults in package folder
                join("/etc", CONFIG_FILE),
                join(expanduser("~"), "." + CONFIG_FILE),
                ]

def parse_config():
    logger.info("Config file search locations: {}".format(CONFIG_CANDIDATES))
    config = ConfigParser()
    found = config.read(CONFIG_CANDIDATES)
    if config.getboolean('logging', 'debug_enabled', fallback=False):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.info('Found config files: {}'.format(sorted(found)))
    return config

def get_config():
    config = parse_config()
    return config

def get_config_dict():
    config = get_config()
    config_dict = {s: dict(config.items(s)) for s in config.sections()}
    logging.info("Config Dict = {}".format(config_dict))
    return config_dict


def get_json_config():
    return json.dumps(get_config_dict(), indent=4, sort_keys=True)


