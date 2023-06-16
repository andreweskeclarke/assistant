from __future__ import annotations

import asyncio
import logging
import typing

import aio_pika

from assistant.agent_router import AgentRouter
from assistant.conversation import Conversation
from assistant.message import Message
from assistant.agent import Agent

LOG = logging.getLogger(__name__)
INPUTS_QUEUE = "inputs"
OUTPUT_EXCHANGE = "outputs"


class RoutingError(Exception):
    pass


async def publish_input(msg: Message, channel: aio_pika.Channel) -> None:
    await channel.default_exchange.publish(
        aio_pika.Message(body=msg.to_json().encode()),
        routing_key=INPUTS_QUEUE,
    )


async def bind_output_handler(handler: typing.Any, channel: aio_pika.Channel) -> None:
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
        connection: aio_pika.Connection,
        router: AgentRouter,
        fallback_agent: Agent,
    ) -> None:
        self.connection = connection
        self.conversation = Conversation()
        self.fallback_agent = fallback_agent
        self.agents: typing.List[Agent] = []
        self.router = router

    def register_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    async def run(self) -> None:
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(INPUTS_QUEUE)
            await queue.consume(self.on_input_message)
            while True:
                await asyncio.sleep(0.1)

    async def on_input_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        async with message.process():
            async with self.connection.channel() as channel:
                msg = Message.from_json(message.body.decode())
                self.conversation.add_user_request(msg.text)

                LOG.info(
                    "Routing (%s %s)",
                    msg.uuid,
                    msg.short_text(),
                )
                agent: typing.Optional[Agent] = await self.router.route(
                    msg, self.conversation, self.agents
                )
                if agent is None:
                    agent = self.fallback_agent
                LOG.info(
                    "Routing to %s (%s %s)",
                    agent.name,
                    msg.uuid,
                    msg.short_text(),
                )

                response: Message = await agent.process_message(msg, self.conversation)
                self.conversation.add_agent_response(response.text)
                exchange: aio_pika.abc.AbstractExchange = await channel.declare_exchange(
                    OUTPUT_EXCHANGE,
                    aio_pika.ExchangeType.FANOUT,
                )
                await exchange.publish(
                    aio_pika.Message(body=response.to_json().encode()),
                    routing_key="",
                )
