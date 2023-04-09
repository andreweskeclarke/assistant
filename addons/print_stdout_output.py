from __future__ import annotations

from assistant.message import Message
from assistant.output import Output


class PrintStdoutOutput(Output):
    async def handle_message(self, msg: Message) -> None:
        print(f"{msg.text}")
