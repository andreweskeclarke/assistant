import git
import openai
import os

# Set your OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]


def chat_gpt_review(code: str):
    # Send the diff and context to GPT-3.5 using the OpenAI API
    prompt = (
        "I am about to make the following change to my code repo. "
        "It is in Git syntax. "
        "Pay close attention to lines starting with '+' or '-'. and focus your feedback on those lines."
        "Can you provide me feedback about code quality, best practices, "
        "using pythonic code, avoiding complexity, consistency, readability, etc?:\n\n"
        f"{code}"
        "\n\n"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful coding assistant who reviews code changes.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def review():
    # Get the git repository and staged changes
    repo = git.Repo(os.getcwd())
    long_diffs = repo.index.diff(
        "HEAD",
        create_patch=True,
        unified=100,
        R=True,
    )
    short_diffs = repo.index.diff("HEAD", create_patch=True, color=True, R=True)
    for long_diff, short_diff in zip(long_diffs, short_diffs):
        print(long_diff.b_path)
        print(short_diff.diff.decode())
        print(chat_gpt_review(long_diff.diff))
        print("\n\n\n")


if __name__ == "__main__":
    review()
