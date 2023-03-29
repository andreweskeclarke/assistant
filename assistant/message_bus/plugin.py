from __future__ import annotations

import logging
import os

import openai

from assistant.message_bus.message import Message

LOG = logging.getLogger(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]


class Plugin:
    @property
    def name(self):
        raise NotImplementedError()

    @property
    def description(self):
        raise NotImplementedError()

    async def process_message(self, message: Message) -> Message:
        raise NotImplementedError()


class EchoPlugin(Plugin):
    @property
    def name(self):
        return "Echo"

    @property
    def description(self):
        return "Echoes the input message"

    async def process_message(self, message: Message) -> Message:
        LOG.debug("Echoing: %s", message)
        return Message(message.text)


class FallbackPlugin(Plugin):
    @property
    def name(self):
        return "Fallback"

    @property
    def description(self):
        return "Forwards the message to ChatGPT"

    async def process_message(self, message: Message) -> Message:
        LOG.debug("Forwarding to ChatGPT: %s", message)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": message.text,
                },
            ],
        )
        return Message(response.choices[0].message.content)
