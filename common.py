import logging


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    c_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(name)s]: %(message)s')
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)
    logger.setLevel(level)
    return logger
