from __future__ import annotations

import logging

from assistant.agent import Agent
from assistant.conversation import Conversation
from assistant.message import Message

LOG = logging.getLogger(__name__)


class EchoAgent(Agent):
    """
    A dead simple Agent that echos messages, useful for testing and debugging.
    """

    @staticmethod
    def name():
        return "Echo"

    @staticmethod
    def description():
        return "Echoes the input message back to the user."

    @staticmethod
    def routing_prompt():
        return "Only use this plugin when the user explicitly wants some text repeated or echoed."

    async def reply_to(self, conversation: Conversation) -> Message:
        message = conversation.last_message()
        LOG.info("Echoing: %s", message)
        return message.evolve()
