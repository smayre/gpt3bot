#!/usr/bin/python3

import os
import openai
from datetime import datetime as dt
from datetime import timedelta
from usagelog import log_usage, get_cost
import sys

COST_LIMIT = 1.0  # USD
LIMIT_PERIOD = 8  # hours

RICH_MODEL = "gpt-4"
POOR_MODEL = "gpt-3.5-turbo"

openai.api_key = os.environ["OPENAI_API_KEY"]


def get_gpt3_completion(messages):
    period_start = dt.now() - timedelta(hours=LIMIT_PERIOD)
    cost = get_cost(start=period_start.timestamp())
    model = RICH_MODEL if cost < COST_LIMIT else POOR_MODEL
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    try:
        log_usage(
            response["created"],
            response["usage"],
            model,
        )
    except BaseException:
        sys.exit(1)
    (choice,) = response["choices"]
    assert choice["message"]["role"] == "assistant"
    return choice["message"]["content"]


if __name__ == "__main__":
    pass
