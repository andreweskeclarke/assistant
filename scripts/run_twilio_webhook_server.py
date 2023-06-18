#!/usr/bin/env python

from __future__ import annotations

import asyncio
import logging

import aio_pika
import tornado.escape
import tornado.web
from twilio.twiml.messaging_response import MessagingResponse

from addons.twilio_sms_client import SmsClientInput, SmsClientOutput, SmsText
from assistant.util.logging import init_logging

LOG = logging.getLogger(__name__)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Lonel.ai")


class SmsHandler(tornado.web.RequestHandler):
    def __init__(self, sms_input_client: SmsClientInput):
        self.sms_input_client = sms_input_client

    async def get(self):
        data = tornado.escape.json_decode(self.request.body)
        LOG.info("SMS received")
        LOG.info(data)
        from_number = data.get("From", None)
        text_message = data.get("Body", None)
        if from_number is not None and text_message is not None:
            await self.sms_input_client.queue.put(
                SmsText(from_number=from_number, text_message=text_message)
            )
        else:
            LOG.error(f"{from_number=} or {text_message=} is None")
        self.write(str(MessagingResponse()))


async def main():
    LOG.info("Connecting to RabbitMQ")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    LOG.info("Configuring Tornado")
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/sms", SmsHandler, dict(sms_input_client=SmsClientInput(connection))),
        ]
    )
    app.listen(8080)
    LOG.info("Running")
    await asyncio.gather(asyncio.Event().wait(), SmsClientOutput(connection).run())


if __name__ == "__main__":
    init_logging(__name__)
    asyncio.run(main())
    LOG.info("Exiting")
