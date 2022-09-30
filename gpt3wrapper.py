#!/usr/bin/python3

import os
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

GPT_PARAMS = dict(
    model="text-davinci-002",
    temperature=0.7,
    max_tokens=128,
    top_p=1,
    frequency_penalty=1,
    presence_penalty=1.5,
)


def get_gpt3_completion(prompt, stop_token, choices=1):
    response = openai.Completion.create(
        prompt=prompt,
        stop=[stop_token],
        n=choices,
        best_of=choices,
        **GPT_PARAMS,
    )
    return [choice["text"] for choice in response["choices"]]


if __name__ == "__main__":
    pass
