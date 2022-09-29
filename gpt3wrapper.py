#!/usr/bin/python3

import os
import openai
import random

openai.api_key = os.environ["OPENAI_API_KEY"]

GPT_PARAMS = dict(
    model="text-davinci-002",
    temperature=0.7,
    max_tokens=128,
    top_p=1,
    frequency_penalty=1,
    presence_penalty=1,
)


def get_gpt3_completion(prompt, stop_token):
    response = openai.Completion.create(
        prompt=prompt,
        stop=[stop_token],
        **GPT_PARAMS,
    )
    choice = random.choice(response["choices"])
    return choice["text"]


if __name__ == "__main__":
    pass
