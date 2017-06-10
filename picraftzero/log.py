import logging
from .config import get_config

debug_enabled = get_config()['logging']['debug_enabled']

if debug_enabled:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

LOG_FORMAT = '%(asctime)s - %(filename)16s:%(lineno)3s - %(funcName)24s() ] - %(levelname)s - %(message)s'
logging.basicConfig(level=log_level, format=LOG_FORMAT)

logger = logging.getLogger(__name__)

