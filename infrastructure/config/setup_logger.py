import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    # Root logger configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),  # logs to console
            RotatingFileHandler(
                "app.log", maxBytes=5_000_000, backupCount=3
            ),  # logs to file
        ],
    )
