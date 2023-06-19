import asyncio
import typing

import pytest

from assistant.agent import Agent
from assistant.assistant import Assistant
from assistant.conversation import Conversation
from assistant.message import Message
from assistant.router import Router


class MockRouter(Router):
    async def route(
        self, conversation: Conversation, agents: typing.List[Agent]
    ) -> Agent:
        return agents[0]


class MockAgent(Agent):
    async def reply_to(self, conversation: Conversation) -> Message:
        return Message(text="Response", source=self.name())


@pytest.mark.asyncio
async def test_assistant():
    router = MockRouter()
    agent = MockAgent()
    conversation = Conversation()
    assistant = Assistant(None, router)  # type: ignore
    assistant.register_agent(agent)
    asyncio.create_task(assistant.run())
    await asyncio.sleep(0)  # Allow the assistant to start running

    # Simulate an input message being received
    input_message = Message(text="Hello", conversation_uuid=conversation.uuid)
    output_message = await assistant.on_message(input_message)

    assert output_message.text == "Response"
    assert output_message.source == "MockAgent"
