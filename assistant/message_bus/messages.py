class Message:
    pass

class IOInput(Message):
    input: str

class IOOutput(Message):
    output: str

class SubscribeRequest(Message):
    id: str
    name: str
    description: str

class SubscribeResponse(Message):
    id: str
    name: str
    description: str
    uuid: str
    topic: str

class 