from __future__ import annotations

import json
import logging
import os
import urllib.request
from enum import Enum

from assistant.conversation import Conversation
from assistant.message import Message
from assistant.plugin import Plugin

LOG = logging.getLogger(__name__)


class AnkiEase(Enum):
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


def _anki_request(action, **params):
    return {"action": action, "params": params, "version": 6}


def _anki_invoke(action, **params):
    request_json = json.dumps(_anki_request(action, **params)).encode("utf-8")
    response = json.load(
        urllib.request.urlopen(
            urllib.request.Request("http://localhost:8765", request_json)
        )
    )
    if len(response) != 2:
        raise RuntimeError("response has an unexpected number of fields")
    if "error" not in response:
        raise RuntimeError("response is missing required error field")
    if "result" not in response:
        raise RuntimeError("response is missing required result field")
    if response["error"] is not None:
        raise RuntimeError(response["error"])
    return response["result"]


class AnkiPlugin(Plugin):
    def __init__(self, deck: str) -> None:
        super().__init__()
        self.deck = deck

    @property
    def name(self):
        return "AnkiPlugin"

    @property
    def description(self):
        return (
            "Connects to the Anki flashcard app, a tool for memorizing flashcards "
            "using spaced repetition."
        )

    @property
    def routing_prompt(self):
        return (
            "Use this plugin when the user asks for Anki explicitly, or if they ask to review cards, "
            "or if they ask to study, or some other similar quizzing request."
        )

    async def process_message(
        self, message: Message, conversation: Conversation
    ) -> Message:
        # The annoying thing about Anki is that it doesn't provide a nice API.
        # We use AnkiConnect, which has to trigger GUI events for some API calls.

        # Kick off deck review, idempotent
        _anki_invoke("guiDeckReview", name=self.deck)
        cards_to_review = _anki_invoke(
            "findCards", query='"deck:' + self.deck + '" is:due'
        )
        if not cards_to_review:
            return Message("Nothing to review today!")

        question_prefix = "Anki Question: "
        answer_prefix = "Anki Answer: "
        last_message = ""
        if conversation.assistant_responses():
            last_message = conversation.assistant_responses()[-1].text

        # Show the user the Anki note answer
        if last_message.startswith(question_prefix):
            answer = _anki_invoke("guiCurrentCard")["fields"]["Back"]["value"]
            return Message(
                answer_prefix
                + answer
                + "\nDifficulty? (reply AGAIN, HARD, GOOD, or EASY)"
            )

        # Mark an answered Anki note as reviewed
        if last_message.startswith(answer_prefix):
            assert _anki_invoke("guiShowAnswer")
            assert _anki_invoke(
                "guiAnswerCard", ease=AnkiEase[message.text.upper()].value
            )

        question = _anki_invoke("guiCurrentCard")["fields"]["Front"]["value"]
        return Message(question_prefix + question)
