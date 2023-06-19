from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from assistant.conversation import Conversation
    from assistant.message import Message


class Agent:
    """
    Agents respond to messages from users using custom domain specific logic.
    User messages are routed to the appropriate plugin(s) to generate a response,
    which is then routed back to the user.
    """

    @classmethod
    def name(cls):
        return cls.__name__

    async def reply_to(self, conversation: Conversation) -> Message:
        raise NotImplementedError()


class EchoAgent(Agent):
    """
    A simple Agent that echos messages, useful for testing and debugging.
    """

    async def reply_to(self, conversation: Conversation) -> Message:
        message = conversation.last_message()
        return message.evolve(source=self.name())
