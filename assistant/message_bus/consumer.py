import json
from typing import Any, Dict, Generator

from kafka import KafkaConsumer


class JsonConsumer:
    def __init__(self, topic: str) -> None:
        self.consumer: KafkaConsumer = KafkaConsumer(
            topic,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            consumer_timeout_ms=10,
        )
        self.topic: str = topic

    def read_message(self) -> Generator[Dict[str, Any], None, None]:
        for message in self.consumer:
            yield message.value


class TextConsumer(JsonConsumer):
    def read_message(self) -> Generator[str, None, None]:
        for message in super().read_message():
            yield message["text"]
