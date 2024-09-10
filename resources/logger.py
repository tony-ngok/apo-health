import logging

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s"


def get_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(FORMAT)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
