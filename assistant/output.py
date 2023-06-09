from __future__ import annotations

import asyncio
import typing

from assistant.assistant import bind_output_handler
from assistant.message import Message

if typing.TYPE_CHECKING:
    import aio_pika


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
            await bind_output_handler(self._message_handler, channel)
            while True:
                await asyncio.sleep(0.1)

    async def _message_handler(self, msg: aio_pika.IncomingMessage):
        async with msg.process():
            message = Message.from_json(msg.body.decode())
            await self.handle_message(message)

    async def handle_message(self, msg: Message) -> None:
        raise NotImplementedError()


class PrintStdoutOutput(Output):
    """A simple output that prints messages to stdout."""

    async def handle_message(self, msg: Message) -> None:
        print(f"{msg.text}")
