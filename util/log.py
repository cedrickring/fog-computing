import logging
import sys

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, stream=sys.stdout)


def get_logger(name: str):
    return logging.getLogger(name)
