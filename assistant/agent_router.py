from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from assistant.agent import Agent
    from assistant.conversation import Conversation
    from assistant.message import Message


class AgentRouter:
    async def route(
        self, message: Message, conversation: Conversation, agents: typing.List[Agent]
    ) -> typing.Optional[Agent]:
        raise NotImplementedError()
