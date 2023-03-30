import asyncio
import logging
import os
from typing import Any

import aio_pika
import openai

from assistant.message import Message

LOG = logging.getLogger(__name__)
INPUTS_QUEUE = "inputs"
OUTPUT_EXCHANGE = "outputs"
openai.api_key = os.environ["OPENAI_API_KEY"]


class RoutingError(Exception):
    pass


class Router:
    def __init__(self, connection: aio_pika.Connection, fallback_plugin: Any):
        self.connection = connection
        self.default_plugin = fallback_plugin
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
                    "You are a smart router. I will send you a list of endpoints, each on a new line, in the form of '<name>: <description>'. "
                    "The final line will be a message, in the form '--- message ---'. "
                    "Identify the endpoint name whose description best matches the message. "
                    "Do not include any explanation, only return the name, following this format without deviation. "
                    "Your response will be a single word, the name of the matching client. "
                ),
            },
            {
                "role": "user",
                "content": (
                    "\n".join(
                        [
                            f"{p.name}: {p.routing_prompt}"
                            for p in self.plugins + [self.default_plugin]
                        ]
                        + [
                            f"{self.default_plugin.name}: This is the default plugin. If no other plugins make sense, select me to reply to the message."
                        ]
                        + [f"--- {msg.text} ---"]
                    )
                ),
            },
        ]
        LOG.info("Routing (%s %s)", msg.uuid, msg.text)
        LOG.info(messages)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=messages,
        )
        plugin_name = response.choices[0].message.content
        plugin = next(
            (p for p in self.plugins if p.name == plugin_name), self.default_plugin
        )
        LOG.info("Routing to %s (%s %s)", plugin.name, msg.uuid, msg.text)
        return plugin
