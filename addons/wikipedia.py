import json
import os

import openai
import requests
import wikipediaapi  # type: ignore

openai.organization = os.getenv("OPENAI_API_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")


class WikipediaEnglishPlugin:
    name = "wikipedia"
    description = (
        "English Wikipedia Plugin. This plugin can query wikipedia and return "
        "the contents of an article. It is useful for answering general knowledge "
        "questions and current event questions. Extracts the main entity from a "
        "message and returns a summary of the Wikipedia page for that entity."
    )

    def __init__(self, message_client):
        self.message_client = message_client
        self.wiki = wikipediaapi.Wikipedia("en")

    def find_wikipedia_page(self, query):
        response = requests.get(
            f"https://en.wikipedia.org/w/rest.php/v1/search/page?q={query}&limit=1",
            timeout=10,
        )
        results = json.loads(response.text)
        key = results["pages"][0]["key"]
        return self.wiki.page(key)

    def extract_entity(self, message):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Extract the main entity from: '{message}'",
                },
            ],
        )
        entity = response["choices"][0]["text"].strip()
        return entity

    def summarize_page(self, page, message):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": (
                        "Summarize the following information in response to this message: "
                        f"'{message}':\n\n"
                        f"{page.title}\n\n{page.summary}\n\n{page.sections}"
                    ),
                },
            ],
        )
        summary = response["choices"][0]["text"].strip()
        return summary

    def process_message(self, message):
        entity = self.extract_entity(message)
        page = self.find_wikipedia_page(entity)
        return self.summarize_page(page, message)

    def run(self):
        while True:
            message = self.message_client.read_message()
            if message:
                answer = self.process_message(message)
                self.message_client.send_message(answer)
