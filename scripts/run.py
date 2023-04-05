from __future__ import annotations

import asyncio
import logging

import aio_pika
from assistant.io.jupyter_assistant_io_client import JupyterAssistantIoClient

from assistant.logs import init_logging
from assistant.plugin.anki import AnkiPlugin
from assistant.plugin.chatgpt_conversational import ChatGptConversationalPlugin
from assistant.plugin.echo import EchoPlugin
from assistant.plugin.jupyter_assistant import JupyterAssistantPlugin
from assistant.plugin_picker.chatgpt_picker import ChatGptPluginPicker
from assistant.routing import Router

LOG = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    LOG.info("Starting")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    router = Router(
        connection,
        plugin_picker=ChatGptPluginPicker(),
        fallback_plugin=ChatGptConversationalPlugin(),
    )
    # router.register_plugin(EchoPlugin())
    router.register_plugin(ChatGptConversationalPlugin())
    # router.register_plugin(AnkiPlugin("Gigadeck"))
    router.register_plugin(JupyterAssistantPlugin())

    jupyter_assistant_server = JupyterAssistantIoClient(connection)

    await asyncio.gather(router.run(), jupyter_assistant_server.run())


if __name__ == "__main__":
    init_logging("router", log_to_stderr=True)
    asyncio.run(main())
