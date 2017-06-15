import logging
import json
from pprint import pformat
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
_config = None

def parse_config():
    logger.info("Config file search locations: {}".format(CONFIG_CANDIDATES))

    config = ConfigParser()
    found = config.read(CONFIG_CANDIDATES)

    logger.info('Merging config from these files:')
    for line in pformat(sorted(found)).split('\n'):
        logger.info(line)

    logger.info("Combined final config is:")
    for line in pformat(get_config_dict(config)).split('\n'):
        logger.info(line)


    if config.getboolean('logging', 'debug_enabled', fallback=False):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return config

def get_config():
    global _config
    if not _config:
        _config = parse_config()
    return _config

def get_config_dict(config):
    config_dict = {s: dict(config.items(s)) for s in config.sections()}
    return config_dict


def get_json_config():
    return json.dumps(get_config_dict(get_config()), indent=4, sort_keys=True)


