from __future__ import annotations

import logging

from assistant.message import Message
from assistant.plugin import Plugin

LOG = logging.getLogger(__name__)


class EchoPlugin(Plugin):
    @property
    def name(self):
        return "Echo"

    @property
    def description(self):
        return "Echoes the input message back to the user."

    @property
    def routing_prompt(self):
        return "Only use this plugin when the user explicitly wants some text repeated or echoed."

    async def process_message(self, message: Message) -> Message:
        LOG.info("Echoing: %s", message)
        return Message(message.text)
