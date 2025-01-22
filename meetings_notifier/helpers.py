import logging
import logging.handlers
import os.path
import shutil
import time
import yaml


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

    ## Silence loggers of some chatty libraries we use
    #urllib_logger = logging.getLogger("urllib3.connectionpool")
    #urllib_logger.setLevel(logging.WARNING)
    #selenium_logger = logging.getLogger("selenium.webdriver.remote.remote_connection")
    #selenium_logger.setLevel(logging.WARNING)
    #kafka_logger = logging.getLogger("kafka")
    #kafka_logger.setLevel(logging.WARNING)

    # Add stderr handler, with provided level
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(stderr_log_lvl)
    logging.getLogger().addHandler(console_handler)

    # Add file rotating handler, with level DEBUG
    rotating_handler = logging.handlers.RotatingFileHandler(
        filename="/tmp/meetings_notifier.log",
        maxBytes=100 * 1000,
        backupCount=2,
    )
    rotating_handler.setFormatter(formatter)
    rotating_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(rotating_handler)

    return logging.getLogger()


def event_to_text(event):
    if event == {}:
        return "No event"
    else:
        return f"When: {event['start'].isoformat()}\nWhat: {event['summary']}\n"


def event_to_log(event):
    if event == {}:
        return "No event"
    else:
        return f"{event['summary']} ({event['start'].isoformat()})"


class MyConfig:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # TODO: Lets use XDG spec for placing config (and logs): https://stackoverflow.com/questions/52670836/standard-log-locations-for-a-cross-platform-application
        user_home_dir = os.path.expanduser("~")
        user_config = os.path.join(user_home_dir, ".meetings_notifier")

        if not os.path.isfile(user_config):
            self.logger.info(f"Copying default config to {user_config}")
            shutil.copyfile("meetings_notifier.config", user_config)

        with open(user_config, "r") as fd:
            self.config = yaml.safe_load(fd)
