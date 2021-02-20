import logging
import logging.config
import os

pwd = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(pwd, 'logger.conf')
logging.config.fileConfig(config_path)
logger = logging.getLogger('log1')
