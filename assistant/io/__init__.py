from __future__ import annotations

import asyncio
import logging
import typing

from assistant.message import Message
from assistant.routing import bind_output_handler, publish_input

if typing.TYPE_CHECKING:
    import aio_pika


LOG = logging.getLogger(__name__)


class Input:
    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    @property
    def name(self) -> str:
        raise NotImplementedError

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            while True:
                text, meta = await self.get_input()
                msg = Message(
                    text=text,
                    source=self.name + ".input",
                    meta=meta,
                )
                LOG.info("Input: %s", msg)
                await publish_input(msg, channel)

    async def get_input(self) -> typing.Tuple[str, dict]:
        raise NotImplementedError()


class Output:
    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            await bind_output_handler(self._message_handler, channel)
            while True:
                await asyncio.sleep(0)

    async def _message_handler(self, msg: aio_pika.IncomingMessage):
        async with msg.process():
            msg = Message.from_json(msg.body.decode())
            LOG.info("Output: %s", msg)
            await self.handle_message(msg)

    async def handle_message(self, msg: Message) -> None:
        raise NotImplementedError()
