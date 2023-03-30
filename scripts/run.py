from __future__ import annotations

import asyncio
import logging

import aio_pika

from assistant.logs import init_logging
from assistant.plugin.echo import EchoPlugin
from assistant.plugin.forgetful_chatgpt import ForgetfulChatGptPlugin
from assistant.routing import Router

LOG = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    LOG.info("Starting")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    router = Router(connection, fallback_plugin=ForgetfulChatGptPlugin())
    router.register_plugin(EchoPlugin())
    await router.run()


if __name__ == "__main__":
    init_logging("router", log_to_stderr=True)
    asyncio.run(main())
