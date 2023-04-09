from __future__ import annotations

import typing

import aioconsole

from assistant.input import Input


class ReadStdinInput(Input):
    @property
    def name(self) -> str:
        return "read-stdin"

    async def get_input(self) -> typing.Tuple[str, dict]:
        message = await aioconsole.ainput("")
        return message, {}
