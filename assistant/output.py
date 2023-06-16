from __future__ import annotations

import asyncio
import logging
import typing

from assistant.assistant import bind_output_handler
from assistant.message import Message

if typing.TYPE_CHECKING:
    import aio_pika


LOG = logging.getLogger(__name__)


class Output:
    """
    The base class for all outputs from the Assistant system.
    Extend this class and implement an awaitable `handle_message()` method.

    Examples could include:
    - a SpeakerOutput, converting text to speech and playing it over speakers
    - a CliOutput, printing messages to a CLI tool via stdout
    - a LogingOutput, sending messages to a python logger
    """

    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            LOG.info("Started output")
            await bind_output_handler(self._message_handler, channel)
            while True:
                await asyncio.sleep(0.1)

    async def _message_handler(self, msg: aio_pika.IncomingMessage):
        async with msg.process():
            msg = Message.from_json(msg.body.decode())
            LOG.info("Output: %s", msg.short_text())
            await self.handle_message(msg)

    async def handle_message(self, msg: Message) -> None:
        raise NotImplementedError()
