from __future__ import annotations

import argparse
import os
import pathlib

import openai

openai.api_key = os.environ["OPENAI_API_KEY"]
GPT3_LONG = "gpt-3.5-turbo-16k"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=pathlib.Path, nargs="+")
    parser.add_argument(
        "--request",
        type=str,
        default="Please review the code and give me feedback and ideas.",
    )
    args = parser.parse_args()
    file_contents = "Below are the contents of most the relevant files:\n"
    assert args.files, "Please provide some files for review"
    for filename in args.files:
        codetype = "python" if filename.suffix == "py" else ""
        code = filename.read_text()
        file_contents += f"\n```{codetype}\n{code}\n```"

    message = (
        f"My request: {args.request}\n"
        "Below is a list of files that I think are relevant to my request, "
        "please take them into consideration."
        f"{file_contents}"
        "OK that should be all the relevant files.\n"
        f"Remember, my request is: {args.request}.\n"
    )
    response = openai.ChatCompletion.create(
        model=GPT3_LONG,
        messages=[
            {
                "role": "system",
                "content": "You are a very senior developer, "
                "eager to help me with coding advice, "
                "identify bugs, "
                "point out more Pythonic code, "
                "suggest style improvements, "
                "give advice on scalability, "
                "and feedback on overall design quality.",
            },
            {"role": "user", "content": message},
        ],
    )
    print(response)
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
