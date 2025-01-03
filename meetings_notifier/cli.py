import argparse
import logging
import signal

from . import my_ui
from . import my_calendar
from . import helpers


def main():
    parser = argparse.ArgumentParser(
        description="Notify loudly when meeting time is comming",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Show debug output",
    )
    args = parser.parse_args()

    if args.debug:
        logger = helpers.setup_logger(logging.DEBUG)
    elif args.verbose:
        logger = helpers.setup_logger(logging.INFO)
    else:
        logger = helpers.setup_logger(logging.WARNING)

    logger.debug(f"Args: {args}")

    # Handle pressing Ctr+C properly, ignored by default
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    calendar = my_calendar.MyCalendar()

    handler = my_ui.MyHandler(calendar)
    handler.run()
