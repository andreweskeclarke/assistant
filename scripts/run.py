from __future__ import annotations

import asyncio
import logging

import aio_pika

from assistant.io.read_stdin_input import ReadStdinInput
from assistant.plugin.echo import EchoPlugin
from assistant.plugin.forgetful_chatgpt import ForgetfulChatGptPlugin
from assistant.routing import Router

LOG = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(name)-50s] %(message)s"
    )
    LOG.info("Starting")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    inputs = ReadStdinInput(connection)
    router = Router(connection, fallback_plugin=ForgetfulChatGptPlugin())
    router.register_plugin(EchoPlugin())
    await asyncio.gather(inputs.run(), router.run())


if __name__ == "__main__":
    asyncio.run(main())
