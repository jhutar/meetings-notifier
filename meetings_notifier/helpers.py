import logging
import logging.handlers
import os.path
import shutil
import time
import xdg.BaseDirectory
import yaml


APP_NAME = "meetings-notifier"
APP_ID = f"com.github.jhutar.{APP_NAME}"
CURRDIR = os.path.dirname(os.path.abspath(__file__))


def setup_logger(stderr_log_lvl):
    """
    Create logger that logs to both stderr and log file but with different log levels
    """
    # Remove all handlers from root logger if any
    logging.basicConfig(
        level=logging.NOTSET,
        handlers=[],
        force=True,
    )
    # Change root logger level from WARNING (default) to NOTSET in order for all messages to be delegated
    logging.getLogger().setLevel(logging.NOTSET)

    # Log message format
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(threadName)s %(levelname)s %(message)s"
    )
    formatter.converter = time.gmtime

    # Add stderr handler, with provided level
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(stderr_log_lvl)
    logging.getLogger().addHandler(console_handler)

    # Add file rotating handler, with level DEBUG
    log_dir = xdg.BaseDirectory.save_cache_path(APP_NAME)
    log_file = os.path.join(log_dir, f"{APP_NAME}.log")
    rotating_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=100 * 1000,
        backupCount=2,
    )
    rotating_handler.setFormatter(formatter)
    rotating_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(rotating_handler)

    logger = logging.getLogger()
    logger.info(f"Logging to {log_file}")
    return logger


class MyConfig:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        default_config = os.path.join(CURRDIR, f"resources/{APP_NAME}.config")

        config_dir = xdg.BaseDirectory.save_config_path(APP_NAME)
        user_config = os.path.join(config_dir, f"{APP_NAME}.config")

        if not os.path.isfile(user_config):
            self.logger.info(f"Copying default config to {user_config}")
            shutil.copyfile(default_config, user_config)

        self.logger.info(f"Loading config from {user_config}")
        with open(user_config, "r") as fd:
            self.config = yaml.safe_load(fd)
