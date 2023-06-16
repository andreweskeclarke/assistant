from __future__ import annotations

import logging
import typing

from assistant.assistant import publish_input
from assistant.message import Message

if typing.TYPE_CHECKING:
    import aio_pika


LOG = logging.getLogger(__name__)


class Input:
    """
    The base class for all inputs into the Assistant system.
    Extend this class and implement an awaitable `get_input()` method.
    get_input() should return an entire utterance, as Assistant is not a streaming system.

    Examples could include:
    - a CliInput, receiving inputs from stdin
    - a MicInput, receiving text covnerted from spoken utterances
    - A DmsInput, receiving inputs from someone's DMs
    """

    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection

    @property
    def name(self) -> str:
        """
        Give each Input class a descriptive, human readable name.
        The name will be used to identify messages arising from the Input subclass, with the field
        `source: "<instance.name>.input"`
        """
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
                LOG.info("Input: %s", msg.short_text())
                await publish_input(msg, channel)

    async def get_input(self) -> typing.Tuple[str, dict]:
        raise NotImplementedError()
