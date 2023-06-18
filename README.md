# Assistant

This is a simple Smart Assistant and Chat Bot. It is currently meant to be a playground for all things ChatGPT, Home Assistant, and Mycroft/OVOS.

# Design

Everything is sent as messages over RabbitMQ. There are a few components:

1. Input modules - code that receives input from a user and forwards the text (CLI, speaking into a microphone, etc)

2. Assistant - Consumes input messages, routes them to an Agent, and broadcasts the outputs

3. Smart Router - a library used by the Assistant to pick the appropriate Agent for an input message

4. Agent - any plugin that can react to an input message (Wikipedia browser, Anki card reviewer, code editor, etc)

5. Output modules - code that can send output back to the user (Text to Speech, CLI, Logging, etc)


# Deployment

I currently run on Azure. For my own memory and future reference:
1. I configured my domain name registrar to use Azure's name servers.
1. I have Azure DNS zones configured to resolve to my public IP address.
2. Azure manages my public IP, pointing to a dedicated VM.
3. On the VM, I manually: installed conda, installed apache, configured apache. cloned my git repo, installed rabbitmq
4. I also installed my dotfiles
5. Then, everything else was normal dev stuff - conda install... etc
