from __future__ import annotations

import json
import uuid
from datetime import datetime

from attr import dataclass, evolve, field


@dataclass
class Message:
    """
    The atomic unit of communication between Users, the Assistant, and Agents.
    Each message corresponds to an utterance in a conversation.
    Remember, the Assistant is here to interact in a human conversation,
    so we should expect human level response times and natural language text
    as the communication protocol.
    """

    text: str = field(default="")
    source: str = field(default="")
    meta: dict = field(factory=dict)
    uuid: str = field(factory=lambda: str(uuid.uuid4()))
    conversation_uuid: str = field(factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(factory=lambda: datetime.utcnow().isoformat())

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        return cls(**json.loads(json_str))

    def __str__(self):
        items = filter(lambda kv: kv[0] != "uuid", vars(self).items())
        desc = ", ".join(
            [f"{self.uuid=}"] + list(map(lambda kv: f"{kv[0]}={kv[1]}", items))
        )
        return f"Message({desc[:100]}...)"

    def evolve(self, *, source: str, **kwargs):
        kwargs["uuid"] = str(uuid.uuid4())
        kwargs["source"] = source
        if "timestamp" in kwargs:
            del kwargs["timestamp"]
        return evolve(self, **kwargs)
