"""
This file contains a utlity function to creater loggers
for all Python scripts in the /Storage directory
"""

import os
import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Creates a log file for with given name in the /Storage/Logs directory.
    The logger records logs with level INFO and uses a standard format for log messages.

    Parameters:
        name (str): Name to be given to the log file.

    Returns:
        logger (logging.Logger) : A configured logging.Logger object.

    Example:
    >>> logger = setup_logger('my_logger')
    >>> logger.info('This is an info message')
    """
    log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file_path = os.path.join(log_directory, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
