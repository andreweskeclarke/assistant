from assistant.message_bus.assistant_manager import AssistantManager
from assistant.message_bus.client import TextMessageClient
from assistant.plugins.cli import CursesClient

if __name__ == "__main__":
    message_client = AssistantManager.subscribe(
        "cli", "Command Line Interface. I am used solely for input and output."
    )
    cli = CursesClient(TextMessageClient(message_client.topic))
    cli.run()
