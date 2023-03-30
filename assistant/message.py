import json
import uuid
from datetime import datetime

from attr import dataclass, field


@dataclass
class Message:
    text: str = field(default="")
    uuid: str = field(factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(factory=lambda: datetime.utcnow().isoformat())

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        return cls(**json.loads(json_str))
