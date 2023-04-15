from __future__ import annotations

import asyncio
import itertools
import logging
import pathlib
import sys

from aiostream import stream

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


async def tail_f(log_file: pathlib.Path):
    with log_file.open("r") as file:
        while line := file.readline():
            pass

        while True:
            line = file.readline()demmmm
            if line:
                yield line.strip()
            else:
                await asyncio.sleep(0)


async def tail_f_logs():
    tails = stream.merge(*[tail_f(log) for log in LOG_DIR.glob("*.log")])
    async with tails.stream() as tail_stream:
        async for line in tail_stream:
            yield line


def tail(log_file: pathlib.Path):
    return log_file.read_text().splitlines()[:-100]


def tail_logs():
    return itertools.chain.from_iterable(tail(log) for log in LOG_DIR.glob("*.log"))
