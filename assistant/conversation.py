from __future__ import annotations

import dataclasses
import typing
import uuid

from assistant.message import Message


@dataclasses.dataclass
class Conversation:
    uuid: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    messages: typing.List[Message] = dataclasses.field(default_factory=list)

    def add(self, message: Message) -> None:
        self.messages.append(message)

    def last_message(self) -> Message:
        """User should check that there is at least one message in the conversation before calling this method."""
        return self.messages[-1]
