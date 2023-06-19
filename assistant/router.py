from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from assistant.agent import Agent
    from assistant.conversation import Conversation


class Router:
    async def route(
        self, conversation: Conversation, agents: typing.List[Agent]
    ) -> Agent:
        raise NotImplementedError()


class RouteToFirstPluginRouter(Router):
    """
    A simple router that always routes to the first plugin, intended for testing and debugging.
    """

    async def route(
        self, conversation: Conversation, agents: typing.List[Agent]
    ) -> Agent:
        return agents[0]
