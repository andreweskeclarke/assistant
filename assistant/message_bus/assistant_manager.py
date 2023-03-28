import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict

import openai

from .client import JsonMessageClient

LOG = logging.getLogger(__name__)
SUBCRIPTIONS_TOPIC = "assistant.subscriptions"
openai.organization = os.getenv("OPENAI_API_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class Client:
    name: str
    client: JsonMessageClient
    client_uuid: str
    topic: str
    description: str

    def read_message(self) -> Any:
        self.client.read_message()

    def send_message(self, *args, **kwargs) -> None:
        self.client.send_message(*args, **kwargs)


class RoutingError(Exception):
    pass


class MessageRouter:
    def __init__(self) -> None:
        self.clients: Dict[str, Client] = {}

    def add(self, client: Client) -> None:
        self.clients[client.client_uuid] = client

    def route_message(self, message: str) -> Client:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a smart router, based on a text message you identify "
                    "the best option out of a list of clients. The best client has a "
                    "description that matches the messages's intent. Infer "
                    "what the message is asking of the broader system and route it to the client most likely to achieve that goal. "
                    "I will send you the message, followed by a list of clients, each on a new line, in the format of '<uuid>: <description>'. "
                    "Do not include any explanation, only return the uuid, following this format without deviation. "
                    "Your response will be a single word, the uuid of the matching client. "
                ),
            },
            {
                "role": "user",
                "content": (
                    "\n\n".join(
                        [message]
                        + [
                            f"{c.client_uuid}: {c.name} {c.description}"
                            for c in self.clients.values()
                        ]
                    )
                ),
            },
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        client_uuid = response.choices[0].message.content
        if client_uuid not in self.clients:
            raise RoutingError(f"Error routing message, AI replied: {client_uuid}")
        return self.clients[client_uuid]


class AssistantManager:
    def __init__(self, router) -> None:
        self.router = router
        self.subscriptions_client = JsonMessageClient(SUBCRIPTIONS_TOPIC)

    def run(self) -> None:
        while True:
            self.handle_subscriptions()
            for client in self.router.clients:
                self.handle_subscriber(client)
            time.sleep(0.1)

    def handle_subscriptions(self) -> None:
        for message in self.subscriptions_client.read_message():
            name = message.value["name"]
            description = message.value["description"]
            client_uuid = str(uuid.uuid4())
            topic = f"{name}.{client_uuid}"
            self.router.add(
                Client(
                    name=name,
                    client=JsonMessageClient(topic),
                    client_uuid=client_uuid,
                    topic=topic,
                    description=description,
                )
            )
            LOG.info("New subscriber %s @%s", name, topic)
            self.subscriptions_client.send_message(
                {
                    "type": "response",
                    "name": name,
                    "uuid": client_uuid,
                    "topic": topic,
                },
            )

    def handle_subscriber(self, client: Client) -> None:
        for message in client.read_message():
            LOG.info('%s: "%s"', client.topic, message)
            self.router.route_messager(message)
