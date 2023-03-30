from __future__ import annotations

import aioconsole

from assistant.io import Input


class ReadStdinInput(Input):
    async def get_input_text(self) -> str:
        message = await aioconsole.ainput("")
        return message
