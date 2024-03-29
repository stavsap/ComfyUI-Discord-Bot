import logging

def get_logger(name, level=logging.INFO):
    _logger = logging.getLogger(name)
    _c_handler = logging.StreamHandler()
    _formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(name)s]: %(message)s')
    _c_handler.setFormatter(_formatter)
    _logger.addHandler(_c_handler)
    _logger.setLevel(level)
    return _logger