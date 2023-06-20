def add(left: str, right: str) -> str:
    """{
        "name": "add",
        "description": "Add two values, left + right.",
        "parameters": {
            "type": "object",
            "properties": {
                "left": {
                    "type": "string",
                    "description": "Left operand."
                },
                "right": {
                    "type": "string",
                    "description": "Right operand."
                }
            },
            "required": ["left", "right"]
        }
    }"""

    return str(float(left) + float(right))


def subtract(left: str, right: str) -> str:
    """{
        "name": "subtract",
        "description": "Subtract two values, left - right.",
        "parameters": {
            "type": "object",
            "properties": {
                "left": {
                    "type": "string",
                    "description": "Left operand."
                },
                "right": {
                    "type": "string",
                    "description": "Right operand."
                }
            },
            "required": ["left", "right"]
        }
    }"""

    return str(float(left) - float(right))


def multiply(left: str, right: str) -> str:
    """{
        "name": "multiply",
        "description": "Multiply two values, left * right.",
        "parameters": {
            "type": "object",
            "properties": {
                "left": {
                    "type": "string",
                    "description": "Left operand."
                },
                "right": {
                    "type": "string",
                    "description": "Right operand."
                }
            },
            "required": ["left", "right"]
        }
    }"""

    return str(float(left) * float(right))


def divide(numerator: str, denominator: str) -> str:
    """{
        "name": "divide",
        "description": "Divide two values, numerator / denominator.",
        "parameters": {
            "type": "object",
            "properties": {
                "numerator": {
                    "type": "string",
                    "description": "Numerator."
                },
                "denominator": {
                    "type": "string",
                    "description": "Denominator."
                }
            },
            "required": ["numerator", "denominator"]
        }
    }"""

    return str(float(numerator) / float(denominator))
