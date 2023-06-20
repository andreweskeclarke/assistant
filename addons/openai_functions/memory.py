# pylint: disable=line-too-long
import typing

memories: typing.Dict[str, str] = {}


def store_in_memory(key: str, value: str) -> str:
    """{
        "name": "store_in_memory",
        "description": "Store a value in memory, for retrieving later on.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Some unique name, that you'll use to retrieve the value later on."
                },
                "value": {
                    "type": "string",
                    "description": "The value to store."
                }
            },
            "required": ["key", "value"]
        }
    }"""

    memories[key] = value
    return f"Ok, stored your value at {key}"


def get_from_memory(key: str) -> str:
    """{
        "name": "get_from_memory",
        "description": "Retrieve a value from memory, that was stored earlier on.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The key of the value to retrieve."
                }
            },
            "required": ["key", "value"]
        }
    }"""

    return memories[key]
