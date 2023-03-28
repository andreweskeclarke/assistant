from assistant.message_bus.assistant_manager import AssistantManager
from assistant.message_bus.client import TextMessageClient
from assistant.plugins.cli import CursesClient

if __name__ == "__main__":
    manager = AssistantManager()
    client = CursesClient(TextMessageClient(manager.subscriptions_message_client.topic))
    client.run()
