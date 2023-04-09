from __future__ import annotations

import logging
import pathlib
import sys

LOG_DIR = pathlib.Path("./logs/")


def log_file_for(module_name: str) -> pathlib.Path:
    return LOG_DIR / f"{module_name}.log"


def init_logging(module_name: str, log_to_stderr: bool = True):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(message)s")

    if log_to_stderr:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.INFO)
        stderr_handler.setFormatter(formatter)
        logger.addHandler(stderr_handler)

    file_handler = logging.FileHandler(str(log_file_for(module_name)))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
