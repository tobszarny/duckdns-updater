import logging
import os
from dotenv import load_dotenv

LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S,'

LOG_MESSAGE_FORMAT = '%(asctime)s %(levelname)s - %(module)s - %(message)s'

DUCKDNS_UPDATER_LOG_FILENAME = 'duckdns-updater.log'

load_dotenv()


def get_log_level() -> int:
    # from logging.XXXXX
    # CRITICAL = 50
    # FATAL = CRITICAL
    # ERROR = 40
    # WARNING = 30
    # WARN = WARNING
    # INFO = 20
    # DEBUG = 10
    # NOTSET = 0
    log_level = os.getenv("LOGGING", "DEBUG").upper()
    match log_level:
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO
        case "WARNING":
            return logging.WARNING
        case "ERROR":
            return logging.ERROR
        case "FATAL":
            return logging.FATAL


def configure_logging() -> logging.Logger:
    segments = str(__file__).split(os.path.sep)
    logger_ = logging.getLogger(segments[-2])
    logging.basicConfig(format=LOG_MESSAGE_FORMAT, encoding='utf-8', level=get_log_level())

    formatter = logging.Formatter(LOG_MESSAGE_FORMAT)

    # Create a file handler
    file_handler = logging.FileHandler(DUCKDNS_UPDATER_LOG_FILENAME)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a formatter and set it for the handlers
    logger_.addHandler(file_handler)
    return logger_
