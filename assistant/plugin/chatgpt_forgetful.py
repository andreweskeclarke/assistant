from __future__ import annotations

import logging
import os

import openai

from assistant.conversation import Conversation
from assistant.message import Message
from assistant.plugin import Plugin

LOG = logging.getLogger(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]


class ChatGptForgetfulPlugin(Plugin):
    @property
    def name(self):
        return "ForgetfulChatGpt"

    @property
    def description(self):
        return "Forwards messages to ChatGPT. This plugin does not retain a memory of any ongoing conversations."

    @property
    def routing_prompt(self):
        return "Use this plugin when the user has a fully stand alone question that contains no references to outside conversations or unclear pronoun references."

    async def process_message(self, message: Message, _: Conversation) -> Message:
        LOG.info("Forwarding to ChatGPT: %s", message)
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
        response_content = response.choices[0].message.content
        LOG.info("ChatGPT replied: '%s'", response_content)
        return Message(response_content)
