from __future__ import annotations

import logging
import os

import openai

from assistant.agent import Agent
from assistant.conversation import Conversation, Utterance
from assistant.message import Message

LOG = logging.getLogger(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]


def chatgpt_message(message: Utterance):
    opeani_source_mapping = {
        "user": "user",
        "agent": "assistant",
        "system": "system",
    }
    return {
        "role": opeani_source_mapping[message.source],
        "content": message.text,
    }


class ChatGptConversationalPlugin(Agent):
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
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *map(chatgpt_message, conversation.utterances),
            ],
        )
        response_content = response.choices[0].message.content
        LOG.info("ChatGPT replied: '%s'", response_content)
        return Message(response_content)
