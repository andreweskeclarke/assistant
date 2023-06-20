from __future__ import annotations

import os

import openai

from assistant.agent import Agent
from assistant.conversation import Conversation
from assistant.message import Message

openai.api_key = os.environ["OPENAI_API_KEY"]
GPT3_LONG = "gpt-3.5-turbo-16k"
GPT4 = "gpt-4-0613"


def chatgpt_message(message: Message):
    return {
        "role": "assistant" if message.source.startswith("ChatGpt") else "user",
        "content": message.text,
    }


class ChatGptForgetfulAgent(Agent):
    async def reply_to(self, conversation: Conversation) -> Message:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                chatgpt_message(conversation.last_message()),
            ],
        )
        return conversation.last_message().evolve(
            text=response.choices[0].message.content, source=self.name()  # type: ignore
        )


class ChatGptConversationalAgent(Agent):
    async def reply_to(self, conversation: Conversation) -> Message:
        response = await openai.ChatCompletion.acreate(
            model=GPT4,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *map(chatgpt_message, conversation.messages),
            ],
        )
        return conversation.last_message().evolve(
            text=response.choices[0].message.content,  # type: ignore
            source=self.name(),
        )


class ChatGptTextingAgent(Agent):
    async def reply_to(self, conversation: Conversation) -> Message:
        response = await openai.ChatCompletion.acreate(
            model=GPT4,
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly, SMS based assistant for a lonely human. "
                    "Reply in a way that is approprate for text messages, including succinctness.",
                },
                *map(chatgpt_message, conversation.messages),
            ],
        )
        return conversation.last_message().evolve(
            text=response.choices[0].message.content,  # type: ignore
            source=self.name(),
        )
