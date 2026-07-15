import logging
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")


def setup_logging(log_file=None):
    """Full detail (requests/responses/errors) to logs/bot.log.

    User-facing output is printed by the CLI, so nothing is logged to the console.
    """
    log_file = log_file or os.path.join(LOG_DIR, "bot.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
