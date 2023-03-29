from __future__ import annotations

import logging
import typing

import aioconsole

from assistant.message_bus.message import Message
from assistant.message_bus.routing import Router

if typing.TYPE_CHECKING:
    import aio_pika

LOG = logging.getLogger(__name__)


class Input:
    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            while True:
                text = await self.get_input_text()
                msg = Message(text)
                LOG.debug("Input: %s", msg)
                await Router.publish_input(msg, channel)

    async def get_input_text(self) -> str:
        raise NotImplementedError()


class CliInput(Input):
    async def get_input_text(self) -> str:
        message = await aioconsole.ainput("Enter message: ")
        return message
