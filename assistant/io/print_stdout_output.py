from __future__ import annotations

from assistant.io import Output
from assistant.message import Message


class PrintStdoutOutput(Output):
    async def handle_message(self, msg: Message) -> None:
        print(f"{msg.text}")
