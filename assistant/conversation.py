import dataclasses
import typing

# Todo: Too hard-coded to the OpenAI definitions of roles and messages


@dataclasses.dataclass
class ConversationMessage:
    role: str
    text: str


@dataclasses.dataclass
class Conversation:
    messages: typing.List[ConversationMessage] = dataclasses.field(default_factory=list)

    def add_assistant_response(self, text: str):
        self.messages.append(ConversationMessage("assistant", text))

    def add_user_request(self, text: str):
        self.messages.append(ConversationMessage("user", text))
