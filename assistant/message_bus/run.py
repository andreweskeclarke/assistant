from __future__ import annotations

import asyncio
import logging

import aio_pika

from assistant.message_bus.input import CliInput
from assistant.message_bus.output import PrintOutput
from assistant.message_bus.plugin import EchoPlugin, FallbackPlugin
from assistant.message_bus.routing import Router

LOG = logging.getLogger(__name__)
INPUTS_QUEUE = "inputs"
OUTPUT_EXCHANGE = "outputs"


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    LOG.info("Starting")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    inputs = CliInput(connection)
    outputs = PrintOutput(connection)
    router = Router(connection, fallback_plugin=FallbackPlugin())
    router.register_plugin(EchoPlugin())
    await asyncio.gather(inputs.run(), router.run(), outputs.run())


if __name__ == "__main__":
    asyncio.run(main())
