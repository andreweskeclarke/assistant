from __future__ import annotations

import asyncio
import logging
import typing

from assistant.message import Message
from assistant.routing import Router

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
                LOG.info("Input: %s", msg)
                await Router.publish_input(msg, channel)

    async def get_input_text(self) -> str:
        raise NotImplementedError()


class Output:
    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            await Router.consume_outputs(self._handle, channel)
            while True:
                await asyncio.sleep(0)

    async def _handle(self, msg: aio_pika.IncomingMessage):
        async with msg.process():
            msg = Message.from_json(msg.body.decode())
            LOG.info("Output: %s", msg)
            await self.handle_message(msg)

    async def handle_message(self, msg: Message) -> None:
        raise NotImplementedError()


class IOClient:
    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            await Router.consume_outputs(self._handle, channel)
            while True:
                await asyncio.sleep(0.01)

        async with self.connection.channel() as channel:
            while True:
                text = await self.get_input_text()
                msg = Message(text)
                LOG.info("Input: %s", msg)
                await Router.publish_input(msg, channel)

    async def _handle(self, msg: aio_pika.IncomingMessage):
        async with msg.process():
            msg = Message.from_json(msg.body.decode())
            LOG.info("Output: %s", msg)
            await self.handle_message(msg)

    async def handle_message(self, msg: Message) -> None:
        raise NotImplementedError()

    async def get_input_text(self) -> str:
        raise NotImplementedError()
