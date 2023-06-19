import asyncio
import logging
import typing
import uuid

import aio_pika
import tornado.ioloop
import tornado.web
import tornado.websocket

from assistant.input import Input
from assistant.message import Message
from assistant.output import Output

LOG = logging.getLogger(__name__)


class _In(Input):
    def __init__(self, connection: aio_pika.Connection):
        super().__init__(connection)
        self.queue = asyncio.Queue()

    @staticmethod
    def name() -> str:
        return "jupyter-assistant-io-client"

    async def get_input(self) -> typing.Tuple[str, str, dict]:
        text = await self.queue.get()
        return text, str(uuid.uuid4()), {}


class _Out(Output):
    def __init__(self, connection: aio_pika.Connection):
        super().__init__(connection)
        self.callback = lambda _: None

    async def handle_message(self, msg: Message) -> None:
        if "jupyter-assistant" in msg.source:
            self.callback(msg)


class WebSocketHandler(
    tornado.websocket.WebSocketHandler
):  # pylint: disable=abstract-method
    def initialize(self, inputs: _In, outputs: _Out):
        self.inputs = inputs  # pylint: disable=attribute-defined-outside-init
        self.outputs = outputs  # pylint: disable=attribute-defined-outside-init
        self.outputs.callback = lambda m: self.write_message(m.to_json())

    def check_origin(self, _):
        return True

    def on_message(self, message):
        LOG.info("Received message from Jupyter assistant: %s", message)
        self.inputs.queue.put_nowait(message)


class JupyterAssistantIoClient:
    def __init__(self, connection) -> None:
        self.inputs = _In(connection)
        self.outputs = _Out(connection)

    async def run(self):
        application = tornado.web.Application(
            [
                (
                    r"/ws",
                    WebSocketHandler,
                    {"inputs": self.inputs, "outputs": self.outputs},
                ),
            ]
        )
        application.listen(8980)
        await asyncio.gather(
            asyncio.Event().wait(), self.inputs.run(), self.outputs.run()
        )
