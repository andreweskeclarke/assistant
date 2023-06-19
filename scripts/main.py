#!/usr/bin/env python

from __future__ import annotations

import asyncio
import logging

import aio_pika

from addons.chatgpt_agents import ChatGptTextingAgent
from assistant.assistant import Assistant
from assistant.conversation_manager import InMemoryConversationsManager
from assistant.router import RouteToFirstPluginRouter
from assistant.util.logging import init_logging

LOG = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    LOG.info("Starting")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    router = Assistant(
        connection,
        router=RouteToFirstPluginRouter(),
        conversations_manager=InMemoryConversationsManager(),
    )
    router.register_agent(ChatGptTextingAgent())
    await asyncio.gather(router.run())


if __name__ == "__main__":
    init_logging("router", log_to_stderr=True)
    asyncio.run(main())
