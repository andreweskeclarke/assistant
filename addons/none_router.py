import logging
import typing


from assistant.agent import Agent
from assistant.agent_router import AgentRouter
from assistant.conversation import Conversation
from assistant.message import Message

LOG = logging.getLogger(__name__)

class NoneRouter(AgentRouter):
    async def route(
        self, message: Message, _: Conversation, plugins: typing.List[Agent]
    ) -> typing.Optional[Agent]:
        return None