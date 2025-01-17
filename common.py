import logging
import os


def get_logger(name, level=logging.INFO):
    envLevel = os.getenv('COMFY_BOT_LOG_LEVEL')
    levelMapping = logging.getLevelNamesMapping()
    if envLevel and envLevel in levelMapping:
        level = levelMapping[envLevel]
    logger = logging.getLogger(name)
    c_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(name)s]: %(message)s')
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)
    logger.setLevel(level)
    return logger
