import asyncio
import logging
import os
from typing import Any

import aio_pika
import openai

from assistant.message_bus.message import Message

LOG = logging.getLogger(__name__)
INPUTS_QUEUE = "inputs"
OUTPUT_EXCHANGE = "outputs"
openai.api_key = os.environ["OPENAI_API_KEY"]


class RoutingError(Exception):
    pass


class Router:
    def __init__(self, connection: aio_pika.Connection, fallback_plugin: Any):
        self.connection = connection
        self.fallback_plugin = fallback_plugin
        self.plugins = []

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    @staticmethod
    async def publish_input(msg: Message, channel: aio_pika.Channel):
        await channel.default_exchange.publish(
            aio_pika.Message(body=msg.to_json().encode()),
            routing_key=INPUTS_QUEUE,
        )

    @staticmethod
    async def consume_outputs(handler: Any, channel: aio_pika.Channel):
        await channel.set_qos(prefetch_count=1)
        exchange = await channel.declare_exchange(
            OUTPUT_EXCHANGE, aio_pika.ExchangeType.FANOUT
        )
        queue = await channel.declare_queue(exclusive=True, auto_delete=True)
        await queue.bind(exchange)
        await queue.consume(handler)

    async def run(self):
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(INPUTS_QUEUE)
            await queue.consume(self.handle_input_message)
            while True:
                await asyncio.sleep(0.01)

    async def handle_input_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            async with self.connection.channel() as channel:
                msg = Message.from_json(message.body.decode())
                plugin = await self.choose_plugin(msg)
                response = await plugin.process_message(msg)
                exchange: aio_pika.Exchange = await channel.declare_exchange(
                    OUTPUT_EXCHANGE, aio_pika.ExchangeType.FANOUT
                )
                await exchange.publish(
                    aio_pika.Message(body=response.to_json().encode()),
                    routing_key="",
                )

    async def choose_plugin(self, msg: Message):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a smart router, based on a text message you identify "
                    "the best option out of a list of clients. The best client has a "
                    "description that matches the messages's intent. Infer "
                    "what the message is asking of the broader system and route it to the client most likely to achieve that goal. "
                    "I will send you the message, followed by a list of clients, each on a new line, in the format of '<name>: <description>'. "
                    "Do not include any explanation, only return the name, following this format without deviation. "
                    "Your response will be a single word, the name of the matching client. "
                ),
            },
            {
                "role": "user",
                "content": (
                    "\n\n".join(
                        [msg.text]
                        + [f"{p.name}: {p.description}" for p in self.plugins]
                    )
                ),
            },
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=messages,
        )
        plugin_name = response.choices[0].message.content
        plugin = next(
            (p for p in self.plugins if p.name == plugin_name), self.fallback_plugin
        )
        return plugin
