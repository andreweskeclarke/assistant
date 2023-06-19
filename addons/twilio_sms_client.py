from __future__ import annotations

import asyncio
import dataclasses
import logging
import os
import typing
import uuid

import aio_pika
from twilio.rest import Client

from assistant.input import Input
from assistant.message import Message
from assistant.output import Output

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
        self.sms_conversation_uuids = {}

    @staticmethod
    def name() -> str:
        return "twilio-sms-io-client"

    async def get_input(self) -> typing.Tuple[str, str, dict]:
        text: SmsText = await self.queue.get()
        if text.from_number not in self.sms_conversation_uuids:
            self.sms_conversation_uuids[text.from_number] = str(uuid.uuid4())
        return (
            text.text_message,
            self.sms_conversation_uuids[text.from_number],
            {
                "phone_number": text.from_number,
            },
        )


class SmsClientOutput(Output):
    async def handle_message(self, msg: Message) -> None:
        if msg.source == SmsClientInput.name():
            LOG.info(msg)
            phone_number = msg.meta["phone_number"]
            text_message = msg.text
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=text_message, from_=TWILIO_PHONE_NUMBER, to=phone_number
            )
            LOG.info("SMS sent to %s: %s", phone_number, text_message)
        else:
            LOG.info("Message dropped: %s", msg)
