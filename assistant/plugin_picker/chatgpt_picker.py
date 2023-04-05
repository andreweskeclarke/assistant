import json
import logging
import os
import typing

import openai

from assistant.conversation import Conversation
from assistant.message import Message
from assistant.plugin import Plugin
from assistant.plugin_picker import PluginPicker

LOG = logging.getLogger(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]


class ChatGptPluginPicker(PluginPicker):
    async def pick(
        self, message: Message, _: Conversation, plugins: typing.List[Plugin]
    ) -> typing.Optional[Plugin]:
        prompt = (
            "I will send you a JSON object with a list of plugins and a request string. "
            "I want you to determine which plugin should be used to handle the request, "
            "according to its description. "
            "If no plugins are a strong match, reply with 'Unknown'. "
            "Only give me the name of the plugin. "
            "Do not include punctuation or any explanation. "
            "Your response will be a single word, the plugin name. "
            "Follow this format without deviation."
        )
        max_length = 3000 - len(prompt)
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
            {
                "role": "user",
                "content": (
                    json.dumps(
                        {
                            "plugins": [
                                {"name": p.name, "description": p.routing_prompt}
                                for p in plugins
                            ],
                            "request": message.text,
                        }
                    )[:-max_length]
                ),
            },
        ]
        LOG.info(messages)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=messages,
        )
        plugin_name = response.choices[0].message.content
        return next((p for p in plugins if p.name == plugin_name), None)
