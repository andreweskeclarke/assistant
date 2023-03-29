from assistant.message_bus.assistant_manager import AssistantManager
from assistant.message_bus.client import TextMessageClient
from assistant.plugins.wikipedia import WikipediaEnglishPlugin

if __name__ == "__main__":
    message_client = AssistantManager.subscribe(
        WikipediaEnglishPlugin.name, WikipediaEnglishPlugin.description
    )
    cli = WikipediaEnglishPlugin(TextMessageClient(message_client.topic))
    cli.run()
