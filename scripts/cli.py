from __future__ import annotations

import asyncio
import logging

import aio_pika

from assistant.io.curses_io_client import CursesIOClient

LOG = logging.getLogger(__name__)


async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    await CursesIOClient(connection).run()


if __name__ == "__main__":
    asyncio.run(main())
