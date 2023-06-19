import typing

import pytest

from assistant.agent import Agent
from assistant.assistant import Assistant
from assistant.conversation import Conversation
from assistant.conversation_manager import InMemoryConversationsManager
from assistant.message import Message
from assistant.router import Router


class MockRouter(Router):
    async def route(
        self, conversation: Conversation, agents: typing.List[Agent]
    ) -> Agent:
        return agents[0]


class MockAgent(Agent):
    async def reply_to(self, conversation: Conversation) -> Message:
        return conversation.last_message().evolve(text="Response", source=self.name())


class ErrorRouter(Router):
    async def route(
        self, conversation: Conversation, agents: typing.List[Agent]
    ) -> Agent:
        raise RuntimeError("Failed to route message.")


class ErrorAgent(Agent):
    async def reply_to(self, conversation: Conversation) -> Message:
        raise RuntimeError("Failed to reply to message.")


@pytest.mark.asyncio
async def test_assistant():
    router = MockRouter()
    agent = MockAgent()
    conversations_manager = InMemoryConversationsManager()
    assistant = Assistant(
        None,  # type: ignore
        router=router,
        conversations_manager=conversations_manager,
    )
    assistant.register_agent(agent)

    # Simulate an input message being received
    input_message = Message(text="Hello")
    output_message = await assistant.on_message(input_message)

    assert output_message.text == "Response"
    assert output_message.source == "MockAgent"
    assert conversations_manager.get_conversation(
        input_message.conversation_uuid
    ).messages == [
        input_message,
        output_message,
    ]


@pytest.mark.asyncio
async def test_assistant_when_router_has_an_error():
    router = ErrorRouter()
    agent = MockAgent()
    conversations_manager = InMemoryConversationsManager()
    assistant = Assistant(
        None,  # type: ignore
        router=router,
        conversations_manager=conversations_manager,
    )
    assistant.register_agent(agent)

    # Simulate an input message being received
    input_message = Message(text="Hello")
    output_message = await assistant.on_message(input_message)

    assert output_message.text == "Routing Error: Failed to route message."
    assert output_message.source == "Assistant"
    assert conversations_manager.get_conversation(
        input_message.conversation_uuid
    ).messages == [input_message]


@pytest.mark.asyncio
async def test_assistant_when_agent_has_an_error():
    router = MockRouter()
    agent = ErrorAgent()
    conversations_manager = InMemoryConversationsManager()
    assistant = Assistant(
        None,  # type: ignore
        router=router,
        conversations_manager=conversations_manager,
    )
    assistant.register_agent(agent)

    # Simulate an input message being received
    input_message = Message(text="Hello")
    output_message = await assistant.on_message(input_message)

    assert output_message.text == "Agent Error: Failed to reply to message."
    assert output_message.source == "Assistant"
    assert conversations_manager.get_conversation(
        input_message.conversation_uuid
    ).messages == [input_message]
