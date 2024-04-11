import logging
import os
import sys


def log_settings() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(os.path.join("log.log"), mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
    )
