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

    def assistant_responses(self):
        return list(filter(lambda m: m.role == "assistant", self.messages))

    def add_assistant_response(self, text: str):
        self.messages.append(ConversationMessage("assistant", text))

    def user_requests(self):
        return list(filter(lambda m: m.role == "user", self.messages))

    def add_user_request(self, text: str):
        self.messages.append(ConversationMessage("user", text))
