# pylint: disable=line-too-long
import json

import requests
import wikipediaapi  # type: ignore


def find_wikipedia_page_key(query: str) -> str:
    """{
        "name": "find_wikipedia_page_key",
        "description": "Search wikipedia for a page, returns a page key for future wikipedia queries like getting the content.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The wikipedia page you want, e.g. 'Napoleon'"
                }
            },
            "required": ["query"]
        }
    }"""

    response = requests.get(
        f"https://en.wikipedia.org/w/rest.php/v1/search/page?q={query}&limit=1",
        timeout=10,
    )
    results = json.loads(response.text)
    page_key = results["pages"][0]["key"]
    return page_key


def list_wikipedia_sections(page_key: str) -> str:
    """{
        "name": "list_wikipedia_sections",
        "description": "Open a wikipedia page and list its sections.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_key": {
                    "type": "string",
                    "description": "The page key, from find_wikipedia_page_key()"
                }
            },
            "required": ["page_key"]
        }
    }"""

    wiki = wikipediaapi.Wikipedia("en")
    wiki_page = wiki.page(page_key)
    return (
        wiki_page.title + ": " + ", ".join(map(lambda s: s.title, wiki_page.sections))
    )


def get_wikipedia_section(page_key: str, section_title: str) -> str:
    """{
        "name": "get_wikipedia_section",
        "description": "Open a wikipedia page and retrieve the contents of a single section.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_key": {
                    "type": "string",
                    "description": "The page key, from find_wikipedia_page_key()"
                },
                "section_title": {
                    "type": "string",
                    "description": "The section title, one of the results from list_wikipedia_sections()"
                }
            },
            "required": ["page_key", "section_title"]
        }
    }"""

    wiki = wikipediaapi.Wikipedia("en")
    wiki_page = wiki.page(page_key)
    section = wiki_page.section_by_title(section_title)
    if section is not None:
        return section.full_text()
    raise ValueError(f"Section {section_title} not found in page {page_key}")


def get_wikipedia_page_summary(page_key: str) -> str:
    """{
        "name": "get_wikipedia_page_summary",
        "description": "Open a wikipedia page and retrieve its summary.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_key": {
                    "type": "string",
                    "description": "The page key, from find_wikipedia_page_key()"
                }
            },
            "required": ["page_key"]
        }
    }"""

    wiki = wikipediaapi.Wikipedia("en")
    wiki_page = wiki.page(page_key)
    return wiki_page.summary
