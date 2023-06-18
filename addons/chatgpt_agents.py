from __future__ import annotations

import logging
import os

import openai

from assistant.agent import Agent
from assistant.conversation import Conversation
from assistant.message import Message

LOG = logging.getLogger(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]


def chatgpt_message(message: Message):
    opeani_source_mapping = {
        "user": "user",
        "agent": "assistant",
        "system": "system",
    }
    return {
        "role": opeani_source_mapping[message.source],
        "content": message.text,
    }


class ChatGptForgetfulPlugin(Agent):
    @staticmethod
    def name():
        return "ForgetfulChatGpt"

    @staticmethod
    def description():
        return "Forwards messages to ChatGPT. This plugin does not retain a memory of any ongoing conversations."

    @staticmethod
    def routing_prompt():
        return "Use this plugin when the user has a fully stand alone question that contains no references to outside conversations or unclear pronoun references."

    async def reply_to(self, conversation: Conversation) -> Message:
        message = conversation.last_message()
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
        return message.evolve(text=response_content)


class ChatGptConversationalPlugin(Agent):
    @staticmethod
    def name():
        return "ChatGptConversational"

    @staticmethod
    def description():
        return "Forwards messages to ChatGPT. This plugin tracks conversations, forwarding the recent conversation history to ChatGPT."

    @staticmethod
    def routing_prompt():
        return "Use this plugin when the user wants to engage on conversation or has general knowledge and advice requests. Only use if a more specific plugin does not match the users request."

    async def reply_to(self, conversation: Conversation) -> Message:
        message = conversation.last_message()
        LOG.info("Forwarding to ChatGPT: %s", message)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *map(chatgpt_message, conversation.messages),
            ],
        )
        response_content = response.choices[0].message.content
        LOG.info("ChatGPT replied: '%s'", response_content)
        return message.evolve(text=response_content)


class ChatGptTextingPlugin(Agent):
    @staticmethod
    def name():
        return "ChatGptTexting"

    @staticmethod
    def description():
        return "Forwards messages to ChatGPT. This plugin tracks conversations, forwarding the recent conversation history to ChatGPT."

    @staticmethod
    def routing_prompt():
        return "Use this plugin when the user wants to engage on conversation or has general knowledge and advice requests."

    async def reply_to(self, conversation: Conversation) -> Message:
        message = conversation.last_message()
        LOG.info("Forwarding to ChatGPT: %s", message)
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly, SMS based assistant for a lonely human. "
                    "Reply in a way that is approprate for text messages, including succinctness.",
                },
                *map(chatgpt_message, conversation.messages),
            ],
        )
        response_content = response.choices[0].message.content
        LOG.info("ChatGPT replied: '%s'", response_content)
        return message.evolve(text=response_content)
