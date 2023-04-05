from __future__ import annotations

import logging
import os

import openai

from assistant.conversation import Conversation, ConversationMessage
from assistant.message import Message
from assistant.plugin import Plugin

LOG = logging.getLogger(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]


def chatgpt_message(message: ConversationMessage):
    return {
        "role": message.role,
        "content": message.text,
    }


class ChatGptConversationalPlugin(Plugin):
    @property
    def name(self):
        return "ChatGptConversational"

    @property
    def description(self):
        return "Forwards messages to ChatGPT. This plugin tracks conversations, forwarding the recent conversation history to ChatGPT."

    @property
    def routing_prompt(self):
        return "Use this plugin when the user wants to engage on conversation or has general knowledge and advice requests. Only use if a more specific plugin does not match the users request."

    async def process_message(
        self, message: Message, conversation: Conversation
    ) -> Message:
        LOG.info("Forwarding to ChatGPT: %s", message)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *map(chatgpt_message, conversation.messages),
            ],
        )
        response_content = response.choices[0].message.content
        LOG.info("ChatGPT replied: '%s'", response_content)
        return Message(response_content)
