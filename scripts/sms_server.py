#!/usr/bin/env python
# pylint: disable=attribute-defined-outside-init
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
    def data_received(self, _):
        pass

    def get(self):
        self.write("Lonel.ai")


class SmsHandler(tornado.web.RequestHandler):
    def initialize(self, sms_input_client: SmsClientInput):
        self.sms_input_client = sms_input_client

    def data_received(self, _):
        pass

    async def get(self):
        from_number = self.get_argument("From", None)
        text_message = self.get_argument("Body", None)
        LOG.info("SMS received from %s: %s", from_number, text_message)
        if from_number is not None and text_message is not None:
            self.sms_input_client.queue.put_nowait(
                SmsText(from_number=from_number, text_message=text_message)
            )
        self.write(str(MessagingResponse()))
        LOG.info("Tornado done processing SMS")


async def main():
    LOG.info("Connecting to RabbitMQ")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    LOG.info("Configuring Tornado")
    sms_input = SmsClientInput(connection)
    sms_output = SmsClientOutput(connection)
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/sms", SmsHandler, {"sms_input_client": sms_input}),
        ]
    )
    app.listen(8080)
    LOG.info("Running")
    await asyncio.gather(sms_input.run(), sms_output.run())


if __name__ == "__main__":
    init_logging(__name__)
    asyncio.run(main())
    LOG.info("Exiting")
