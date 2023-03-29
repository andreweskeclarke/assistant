from __future__ import annotations

import asyncio
import logging
import typing

from assistant.message_bus.message import Message
from assistant.message_bus.routing import Router

if typing.TYPE_CHECKING:
    import aio_pika


LOG = logging.getLogger(__name__)


class Output:
    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            await Router.consume_outputs(self._handle, channel)
            while True:
                await asyncio.sleep(0.01)

    async def _handle(self, msg: aio_pika.IncomingMessage):
        async with msg.process():
            msg = Message.from_json(msg.body.decode())
            LOG.debug("Output: %s", msg)
            await self.handle_message(msg)

    async def handle_message(self, msg: Message) -> None:
        raise NotImplementedError()


class PrintOutput(Output):
    async def handle_message(self, msg: Message) -> None:
        print(f"{msg.text}")
