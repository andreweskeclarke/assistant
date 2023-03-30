from __future__ import annotations

from assistant.message import Message


class Plugin:
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
