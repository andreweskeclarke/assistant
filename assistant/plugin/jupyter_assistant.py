from __future__ import annotations

import logging
import os

import openai

from assistant.conversation import Conversation
from assistant.message import Message
from assistant.plugin import Plugin

LOG = logging.getLogger(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]


def add_comment_markers(text):
    # GPT still returns commentary even when I request it not to
    # This code can prefix those comments with '#', assuming the text is mostly well formatted

    robot_is_commenting = True
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("```"):
            lines[i] = "# " + line
            robot_is_commenting = not robot_is_commenting
        elif robot_is_commenting:
            lines[i] = "# " + line
    return "\n".join(lines)


class JupyterAssistantPlugin(Plugin):
    @property
    def name(self):
        return "JupyterAssistant"

    @property
    def description(self):
        return "This Jupyter assistant can help uses auto complete their code."

    @property
    def routing_prompt(self):
        return "Receives Jupyter code, cells, and suggestions and auto completes a new cell based on the user request."

    async def process_message(self, message: Message, _b: Conversation) -> Message:
        prompt = "The following is some Jupyter python code, its outputs, and a comment asking you to fill in some code. Please return the python code wrapped as ```python```:\n"
        max_length = 3000 - len(prompt)

        LOG.info("Forwarding to ChatGPT: %s", message)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful Python Jupyter coding assistant.",
                },
                {
                    "role": "user",
                    "content": prompt + message.text[-max_length:],
                },
            ],
        )
        response_content = add_comment_markers(response.choices[0].message.content)
        LOG.info("ChatGPT replied: '%s'", response_content)
        return Message(
            text=response_content,
            source="jupyter-assistant-plugin",
            meta={"originating_source": message.source},
        )
