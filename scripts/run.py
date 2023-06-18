#!/usr/bin/env python

from __future__ import annotations

import asyncio
import logging

import aio_pika

from addons.chatgpt_texting import ChatGptTextingPlugin
from addons.none_router import NoneRouter
from assistant.assistant import Assistant
from assistant.util.logging import init_logging

LOG = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    LOG.info("Starting")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    router = Assistant(
        connection,
        router=NoneRouter(),
        fallback_agent=ChatGptTextingPlugin(),
    )

    await asyncio.gather(router.run())


if __name__ == "__main__":
    init_logging("router", log_to_stderr=True)
    asyncio.run(main())
