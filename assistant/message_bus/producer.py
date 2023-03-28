import json
from typing import Any, Dict

from kafka import KafkaProducer


class JsonProducer:
    def __init__(self, topic: str) -> None:
        self.producer = KafkaProducer(
            value_serializer=lambda m: json.dumps(m).encode("utf-8")
        )
        self.topic = topic

    def send_message(self, message: Dict[str, Any]) -> None:
        self.producer.send(self.topic, message)


class TextProducer(JsonProducer):
    def send_message(self, message: str) -> None:
        message = {"text": message}
        super().send_message(message)
