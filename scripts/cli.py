from __future__ import annotations

import asyncio
import logging

import aio_pika

from addons.curses_io_client import CursesIOClient
from assistant.util.logging import init_logging

LOG = logging.getLogger(__name__)


async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    await CursesIOClient(connection).run()


if __name__ == "__main__":
    init_logging("cli", log_to_stderr=False)
    asyncio.run(main())
