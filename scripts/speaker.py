from __future__ import annotations

import asyncio
import logging

import aio_pika

from addons.speak_output import SpeakOutput
from assistant.util.logging import init_logging

LOG = logging.getLogger(__name__)


async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    await SpeakOutput(connection).run()


if __name__ == "__main__":
    init_logging("speaker")
    LOG.info("Initializing speaker")
    asyncio.run(main())
