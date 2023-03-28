import logging

from assistant.message_bus.assistant_manager import AssistantManager

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    manager = AssistantManager()
    manager.run()
