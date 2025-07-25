import logging.config
import os

log_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "SPYDIR.log")
logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s: %(message)s"},
        "detailed": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": log_file_path,
            "maxBytes": 50000,
            "backupCount": 0,
            "delay": True,
        },
    },
    "loggers": {"root": {"level": "DEBUG", "handlers": ["stderr", "file"]}},
}

logging.config.dictConfig(logger_config)
logger = logging.getLogger("SPYDIR")
