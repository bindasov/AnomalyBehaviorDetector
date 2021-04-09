from logging import basicConfig, getLogger
from server.common.conf import config


def get_logger(name=None, loglevel=config.LOGLEVEL, filename=config.LOGFILE):
    basicConfig(filename=filename, level=loglevel, format='%(asctime)s-%(levelname)s-[%(name)s]: %(message)s')
    return getLogger(name or 'detector')
