from __future__ import annotations

import asyncio
import logging
import typing

import aio_pika

from assistant.conversation import Conversation
from assistant.conversation_manager import ConversationsManager
from assistant.message import Message

if typing.TYPE_CHECKING:
    from assistant.agent import Agent
    from assistant.router import Router

LOG = logging.getLogger(__name__)
INPUTS_QUEUE = "inputs"
OUTPUT_EXCHANGE = "outputs"


class RoutingError(Exception):
    pass


async def publish_input(msg: Message, channel: aio_pika.abc.AbstractChannel) -> None:
    await channel.default_exchange.publish(
        aio_pika.Message(body=msg.to_json().encode()),
        routing_key=INPUTS_QUEUE,
    )


async def bind_output_handler(
    handler: typing.Any, channel: aio_pika.abc.AbstractChannel
) -> None:
    await channel.set_qos(prefetch_count=1)
    exchange = await channel.declare_exchange(
        OUTPUT_EXCHANGE, aio_pika.ExchangeType.FANOUT
    )
    queue = await channel.declare_queue(exclusive=True, auto_delete=True)
    await queue.bind(exchange)
    await queue.consume(handler)


class Assistant:
    def __init__(
        self,
        connection: aio_pika.abc.AbstractRobustConnection,
        router: Router,
        conversations_manager: ConversationsManager,
    ) -> None:
        self.connection = connection
        self.conversations_manager: ConversationsManager = conversations_manager
        self.agents: typing.List[Agent] = []
        self.router = router

    def register_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(INPUTS_QUEUE)
            await queue.consume(self.on_aiopika_message)
            await asyncio.Event().wait()

    async def on_aiopika_message(
        self, q_message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        async with q_message.process():
            async with self.connection.channel() as channel:
                msg = Message.from_json(q_message.body.decode())
                response_message = await self.on_message(msg)
                exchange: aio_pika.abc.AbstractExchange = (
                    await channel.declare_exchange(
                        OUTPUT_EXCHANGE,
                        aio_pika.ExchangeType.FANOUT,
                    )
                )
                await exchange.publish(
                    aio_pika.Message(body=response_message.to_json().encode()),
                    routing_key="",
                )

    async def on_message(self, message: Message) -> Message:
        conversation: Conversation = await self.conversations_manager.add_message(
            message
        )

        try:
            agent: Agent = await self.router.route(conversation, self.agents)
            LOG.info('Routing message %s to agent "%s"', message, agent.name)
        except Exception as exception:  # pylint: disable=broad-exception-caught
            LOG.exception(exception)
            return message.evolve(
                source="Assistant", text=f"Routing Error: {exception}"
            )

        try:
            response: Message = await agent.reply_to(conversation)
            LOG.info("Agent replied with %s", response)
        except Exception as exception:  # pylint: disable=broad-exception-caught
            LOG.exception(exception)
            return message.evolve(source="Assistant", text=f"Agent Error: {exception}")

        await self.conversations_manager.add_message(response)
        return response
