# Assistant

This is a simple Smart Assistant and Chat Bot. It is currently meant to be a playground for all things ChatGPT, Home Assistant, and Mycroft/OVOS.

# Design

Everything is sent as messages over RabbitMQ. There are a few components:

1. Input modules - code that receives input from a user and forwards the text (CLI, speaking into a microphone, etc)

2. Assistant - Consumes input messages, routes them to an Agent, and broadcasts the outputs

3. Smart Router - a library used by the Assistant to pick the appropriate Agent for an input message

4. Agent - any plugin that can react to an input message (Wikipedia browser, Anki card reviewer, code editor, etc)

5. Output modules - code that can send output back to the user (Text to Speech, CLI, Logging, etc)
