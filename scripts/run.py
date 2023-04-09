from __future__ import annotations

import asyncio
import logging

import aio_pika

from addons.chatgpt_conversational import ChatGptConversationalPlugin
from addons.chatgpt_picker import ChatGptPluginPicker
from addons.jupyter_assistant import JupyterAssistantPlugin
from addons.jupyter_assistant_io_client import JupyterAssistantIoClient
from assistant.assistant import Assistant
from assistant.util.logging import init_logging

LOG = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    LOG.info("Starting")
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    router = Assistant(
        connection,
        plugin_picker=ChatGptPluginPicker(),
        fallback_plugin=ChatGptConversationalPlugin(),
    )
    router.register_plugin(JupyterAssistantPlugin())

    jupyter_assistant_server = JupyterAssistantIoClient(connection)

    await asyncio.gather(router.run(), jupyter_assistant_server.run())


if __name__ == "__main__":
    init_logging("router", log_to_stderr=True)
    asyncio.run(main())
