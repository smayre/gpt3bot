#!/usr/bin/python3

import os
import openai
import random

openai.api_key = os.environ["OPENAI_API_KEY"]

MODEL = "text-davinci-002"
TEMPERATURE = 0.7


def get_gpt3_completion(prompt, stop_token, model=MODEL, temperature=TEMPERATURE):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=[stop_token],
    )
    choice = random.choice(response["choices"])
    return choice["text"]




if __name__ == "__main__":
    pass
