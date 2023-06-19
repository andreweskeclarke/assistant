import csv
import pathlib
import typing
from abc import ABC, abstractmethod

import aiocsv
import aiofiles
from attr import asdict, fields_dict

from assistant.conversation import Conversation
from assistant.message import Message


class ConversationsManager(ABC):
    @abstractmethod
    async def add_message(self, message: Message) -> Conversation:
        pass

    @abstractmethod
    def get_conversation(self, uuid: str) -> Conversation:
        pass


class InMemoryConversationsManager(ConversationsManager):
    def __init__(self) -> None:
        self.conversations: typing.Dict[str, Conversation] = {}

    async def add_message(self, message: Message) -> Conversation:
        conversation = self.get_conversation(message.conversation_uuid)
        conversation.add(message)
        return conversation

    def get_conversation(self, uuid: str) -> Conversation:
        if uuid not in self.conversations:
            self.conversations[uuid] = Conversation(uuid=uuid)
        return self.conversations[uuid]


class CsvConversationsManager(ConversationsManager):
    def __init__(self, csv_file_path: str | pathlib.Path) -> None:
        self.csv_file_path: pathlib.Path = pathlib.Path(csv_file_path)
        self.conversations: typing.Dict[str, Conversation] = {}
        self._load_conversations()

    def _load_conversations(self) -> None:
        try:
            with open(self.csv_file_path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    msg = Message(**row)  # type: ignore
                    if msg.conversation_uuid not in self.conversations:
                        self.conversations[msg.conversation_uuid] = Conversation(
                            uuid=msg.conversation_uuid
                        )
                    self.conversations[msg.conversation_uuid].add(msg)
        except FileNotFoundError:
            self.csv_file_path.touch()

    async def add_message(self, message: Message) -> Conversation:
        conversation = self.get_conversation(message.conversation_uuid)
        conversation.add(message)
        await self._append_to_csv(message)
        return conversation

    async def _append_to_csv(self, message: Message) -> None:
        async with aiofiles.open(
            self.csv_file_path, "a", newline="", encoding="utf-8"
        ) as afp:
            writer = aiocsv.AsyncDictWriter(
                afp,
                fieldnames=list(fields_dict(Message).keys()),  # type: ignore
            )
            await writer.writerow(asdict(message))  # type: ignore

    def get_conversation(self, uuid: str) -> Conversation:
        if uuid not in self.conversations:
            self.conversations[uuid] = Conversation(uuid=uuid)
        return self.conversations[uuid]
