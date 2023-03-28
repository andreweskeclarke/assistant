import logging
import time
import uuid
from typing import Any, Dict

from .client import JsonMessageClient

LOG = logging.getLogger(__name__)
SUBCRIPTIONS_TOPIC = "assistant.subscriptions"


class Subscriber:
    def __init__(
        self, client: JsonMessageClient, subscriber_uuid: str, description: str
    ) -> None:
        self.client = client
        self.subscriber_uuid = subscriber_uuid
        self.description = description

    def read_message(self) -> Any:
        self.client.read_message()

    def send_message(self, *args, **kwargs) -> None:
        self.client.send_message(*args, **kwargs)


class AssistantManager:
    def __init__(self) -> None:
        self.subscribers: Dict[str, JsonMessageClient] = {}
        self.subscriptions_message_client = JsonMessageClient(SUBCRIPTIONS_TOPIC)

    def run(self) -> None:
        while True:
            self.handle_subscriptions()
            for subscriber, client in self.subscribers.items():
                self.handle_subscriber(subscriber, client)
            time.sleep(0.1)

    def handle_subscriptions(self) -> None:
        for message in self.subscriptions_message_client.read_message():
            name = message.value["name"]
            description = message.value["description"]
            subscriber_uuid = str(uuid.uuid4())
            subscriber_topic = f"{name}.{subscriber_uuid}"
            self.subscribers[subscriber_topic] = Subscriber(
                client=JsonMessageClient(subscriber_topic),
                subscriber_uuid=subscriber_uuid,
                description=description,
            )
            LOG.info("New subscriber %s @%s", name, subscriber_topic)
            self.subscribers[subscriber_topic].send_message(
                subscriber_topic, {"message": f"Welcome to {name}!"}
            )
            self.subscriptions_message_client.send_message(
                {
                    "subscriber_uuid": subscriber_uuid,
                    "subscriber_topic": subscriber_topic,
                },
            )

    def handle_subscriber(
        self, subscriber_topic: str, client: JsonMessageClient
    ) -> None:
        for message in client.read_message():
            client.send_message({"message": message})
            LOG.info('%s: "%s"', subscriber_topic, message)
