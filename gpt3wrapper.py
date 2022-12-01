#!/usr/bin/python3

import os
import openai
from datetime import datetime as dt
from datetime import timedelta
from usagelog import log_usage, get_cost
import sys

COST_LIMIT = 0.10  # USD
LIMIT_PERIOD = 4  # hours

RICH_MODEL = "text-davinci-003"
POOR_MODEL = "text-babbage-001"

openai.api_key = os.environ["OPENAI_API_KEY"]

GPT_PARAMS = dict(
    temperature=0.9,
    max_tokens=128,
    top_p=1,
    frequency_penalty=1,
    presence_penalty=1.5,
)


def get_gpt3_completion(prompt, stop_token):
    period_start = dt.now() - timedelta(hours=LIMIT_PERIOD)
    cost = get_cost(start=period_start.timestamp())
    model = RICH_MODEL if cost < COST_LIMIT else POOR_MODEL
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        stop=[stop_token],
        **GPT_PARAMS,
    )
    try:
        log_usage(
            response["created"],
            response["usage"]["total_tokens"],
            response["model"],
        )
    except BaseException:
        sys.exit(1)
    (choice,) = response["choices"]
    return choice["text"]


if __name__ == "__main__":
    pass
