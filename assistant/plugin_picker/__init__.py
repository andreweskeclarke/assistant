import typing

from assistant.conversation import Conversation
from assistant.message import Message
from assistant.plugin import Plugin


class PluginPicker:
    async def pick(
        self, message: Message, conversation: Conversation, plugins: typing.List[Plugin]
    ) -> typing.Optional[Plugin]:
        raise NotImplementedError()
