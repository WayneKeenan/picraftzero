import logging
LOG_FORMAT = '%(asctime)s - %(filename)16s:%(lineno)3s - %(funcName)24s() ] - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
logger = logging.getLogger('picraftzero')
logger.setLevel(logging.INFO)
