import os

import twilio.rest

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = twilio.rest.Client(account_sid, auth_token)

numbers = {
    "andrew": "+19012305184",
    "assistant": "+18883089729",
}

message = client.messages.create(
    body="Hi, my name is Tobias. How can I help you?",
    from_=numbers["assistant"],
    to=numbers["andrew"],
)

print(message)
