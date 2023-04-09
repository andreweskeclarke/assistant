from __future__ import annotations

import dataclasses
import typing

AGENT = "agent"
USER = "user"


@dataclasses.dataclass
class Utterance:
    source: str
    text: str


@dataclasses.dataclass
class Conversation:
    utterances: typing.List[Utterance] = dataclasses.field(default_factory=list)

    def agent_responses(self):
        return list(filter(lambda m: m.source == AGENT, self.utterances))

    def add_agent_response(self, text: str):
        self.utterances.append(Utterance(AGENT, text))

    def user_requests(self):
        return list(filter(lambda m: m.source == USER, self.utterances))

    def add_user_request(self, text: str):
        self.utterances.append(Utterance(USER, text))
