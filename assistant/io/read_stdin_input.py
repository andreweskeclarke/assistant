from __future__ import annotations

import aioconsole

from assistant.io import Input

import typing


class ReadStdinInput(Input):
    @property
    def name(self) -> str:
        return "read-stdin"

    async def get_input(self) -> typing.Tuple[str, dict]:
        message = await aioconsole.ainput("")
        return message, {}
