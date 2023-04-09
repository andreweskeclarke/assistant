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

    The name, description, and routing prompt are all used to route messages to agents.
    """

    @property
    def name(self):
        raise NotImplementedError()

    @property
    def description(self):
        raise NotImplementedError()

    @property
    def routing_prompt(self):
        raise NotImplementedError()

    async def process_message(
        self, message: Message, conversation: Conversation
    ) -> Message:
        raise NotImplementedError()
