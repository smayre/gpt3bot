#!/usr/bin/python3

import os
import openai
from datetime import datetime as dt
import random

openai.api_key = os.environ["OPENAI_API_KEY"]

MODEL = "text-davinci-002"
TEMPERATURE = 0.7
STOP_TOKEN = "<EOT>"


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


def generate_reply(message_history, bot_userid, stop_token=STOP_TOKEN):
    """Create a prompt for GPT-3 by converting a Slack conversation
    history into a chat log. Append the STOP_TOKEN to the end of each
    message so that (hopefully) GPT-3 will do the same, which we then
    use to cut off GPT-3's completion. Otherwise GPT-3 may produce a fake
    conversation with itself."""

    messages = [
        (dt.fromtimestamp(float(msg["ts"])), msg["user"], msg["text"])
        for msg in message_history
        if msg["text"].strip() != f"<@{bot_userid}>"
    ]
    messages.sort(key=lambda ts, _, _: ts)
    chatlog = [
        f"{ts.isoformat()} {userid}: {text}{stop_token}"
        for ts, userid, text in messages
    ]
    now = dt.now().isoformat()
    chatlog.append(f"{now} {bot_userid}:")
    prompt = "\n".join(chatlog)
    gpt3_reply = get_gpt3_completion(prompt, stop_token)
    return gpt3_reply


if __name__ == "__main__":
    pass
