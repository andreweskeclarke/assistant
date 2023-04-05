import asyncio
import logging
import typing

import aio_pika

from assistant.conversation import Conversation
from assistant.message import Message
from assistant.plugin import Plugin
from assistant.plugin_picker import PluginPicker

LOG = logging.getLogger(__name__)
INPUTS_QUEUE = "inputs"
OUTPUT_EXCHANGE = "outputs"


class RoutingError(Exception):
    pass


async def publish_input(msg: Message, channel: aio_pika.Channel):
    await channel.default_exchange.publish(
        aio_pika.Message(body=msg.to_json().encode()),
        routing_key=INPUTS_QUEUE,
    )


async def bind_output_handler(handler: typing.Any, channel: aio_pika.Channel):
    await channel.set_qos(prefetch_count=1)
    exchange = await channel.declare_exchange(
        OUTPUT_EXCHANGE, aio_pika.ExchangeType.FANOUT
    )
    queue = await channel.declare_queue(exclusive=True, auto_delete=True)
    await queue.bind(exchange)
    await queue.consume(handler)


class Router:
    def __init__(
        self,
        connection: aio_pika.Connection,
        plugin_picker: PluginPicker,
        fallback_plugin: typing.Any,
    ):
        self.connection = connection
        self.conversation = Conversation()
        self.default_plugin = fallback_plugin
        self.plugins = []
        self.plugin_picker = plugin_picker

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    async def run(self):
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(INPUTS_QUEUE)
            await queue.consume(self.on_input_message)
            while True:
                await asyncio.sleep(0)

    async def on_input_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            async with self.connection.channel() as channel:
                msg = Message.from_json(message.body.decode())
                self.conversation.add_user_request(msg.text)

                LOG.info("Routing (%s %s)", msg.uuid, msg.text)
                plugin: typing.Optional[Plugin] = await self.plugin_picker.pick(
                    msg, self.conversation, self.plugins
                )
                if plugin is None:
                    plugin = self.default_plugin
                LOG.info("Routing to %s (%s %s)", plugin.name, msg.uuid, msg.text)

                response: Message = await plugin.process_message(msg, self.conversation)
                self.conversation.add_assistant_response(response.text)
                exchange: aio_pika.Exchange = await channel.declare_exchange(
                    OUTPUT_EXCHANGE, aio_pika.ExchangeType.FANOUT
                )
                await exchange.publish(
                    aio_pika.Message(body=response.to_json().encode()),
                    routing_key="",
                )
