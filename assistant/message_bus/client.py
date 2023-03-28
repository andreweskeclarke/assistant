import abc
from typing import Any, Dict, Generator, Generic, TypeVar

from .consumer import JsonConsumer, TextConsumer
from .producer import JsonProducer, TextProducer

MessageType = TypeVar("MessageType")  # pylint: disable=invalid-name


class MessageClient(Generic[MessageType], abc.ABC):
    @abc.abstractmethod
    def __init__(self, topic: str) -> None:
        pass

    @abc.abstractmethod
    def read_message(self) -> Generator[MessageType, None, None]:
        raise NotImplementedError("read_message must be implemented in a subclass.")

    @abc.abstractmethod
    def send_message(self, message: MessageType) -> None:
        raise NotImplementedError("send_message must be implemented in a subclass.")


class JsonMessageClient(MessageClient[Dict[str, Any]]):
    def __init__(self, topic: str) -> None:
        self.topic = topic
        self.consumer: JsonConsumer[Dict[str, Any]] = JsonConsumer(topic)
        self.producer: JsonProducer[Dict[str, Any]] = JsonProducer(topic)

    def read_message(self) -> Generator[Dict[str, Any], None, None]:
        yield from self.consumer.read_message()

    def send_message(self, message: Dict[str, Any]) -> None:
        self.producer.send_message(message)


class TextMessageClient(MessageClient[str]):
    def __init__(self, topic: str) -> None:
        self.consumer: TextConsumer = TextConsumer(topic)
        self.producer: TextProducer = TextProducer(topic)

    def read_message(self) -> Generator[str, None, None]:
        yield from self.consumer.read_message()

    def send_message(self, message: str) -> None:
        self.producer.send_message(message)
