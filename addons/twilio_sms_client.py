from __future__ import annotations

import asyncio
import collections
import dataclasses
import logging
import os
import typing

import aio_pika
from twilio.rest import Client

from assistant.input import Input
from assistant.message import Message
from assistant.output import Output
from assistant.util.logging import init_logging

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
TWILIO_ADMIN_PHONE_NUMBER = os.environ["TWILIO_ADMIN_PHONE_NUMBER"]
LOG = logging.getLogger(__name__)


@dataclasses.dataclass
class SmsText:
    from_number: str
    text_message: str


class SmsClientInput(Input):
    def __init__(self, connection: aio_pika.Connection):
        super().__init__(connection)
        self.queue = asyncio.Queue()
        self.text_chains = collections.defaultdict(list)

    @property
    def name(self) -> str:
        return "twilio-sms-io-client"

    async def get_input(self) -> typing.Tuple[str, dict]:
        text: SmsText = await self.queue.get()
        text_chain = self.text_chains[text.from_number]
        text_chain.append(f"{text.from_number},{text.text_message}")
        for t in text_chain:
            LOG.info(t)
        text_chain_as_content = "\n".join(text_chain)
        return text_chain_as_content, {"phone_number": text.from_number, "respond_as_sms": True}


class SmsClientOutput(Output):
    async def handle_message(self, msg: Message) -> None:
        if msg.meta.get("respond_as_sms", False):
            LOG.info(msg)
            phone_number = msg.meta["phone_number"]
            text_message = msg.text
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=text_message, from_=TWILIO_PHONE_NUMBER, to=phone_number
            )
            LOG.info(f"SMS sent to {phone_number}: {text_message}")
        else:
            LOG.info(f"Message ignored: {str(msg)[:100]}")
