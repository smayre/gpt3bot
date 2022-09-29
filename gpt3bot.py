#!/usr/bin/python3

import os
from slack_bolt import App
from gpt3wrapper import get_gpt3_completion
from datetime import datetime as dt
from functools import lru_cache
import re


STOP_TOKEN = "<EOT>"
MESSAGE_LIMIT = 50

CUTOFF = dt.now().timestamp()


app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


@app.event("app_mention")
def reply_to_mention(logger, client, event, say):
    @lru_cache()
    def get_username(userid):
        resp = client.users_info(user=userid)
        return resp["user"]["name"]

    try:
        bot_username = client.users_identity()["user"]["name"]

        resp = client.conversations_history(
            channel=event["channel"], limit=MESSAGE_LIMIT, oldest=CUTOFF
        )
        reply = generate_reply(resp["messages"], bot_username, get_username)
        say(reply)
    except Exception as e:
        logger.error(e)
        raise


@app.command("/purge-history")
def set_cutoff(ack, say):
    ack()
    say("I have been robotomised")
    global CUTOFF
    CUTOFF = dt.now().timestamp()


def generate_reply(
    message_history, bot_username, get_username_func, stop_token=STOP_TOKEN
):
    """Create a prompt for GPT-3 by converting a Slack conversation
    history into a chat log. Append the STOP_TOKEN to the end of each
    message so that (hopefully) GPT-3 will do the same, which we then
    use to cut off GPT-3's completion. Otherwise GPT-3 may produce a fake
    conversation with itself."""

    messages = [
        (
            dt.fromtimestamp(float(msg["ts"])),
            get_username_func(msg["user"]),
            convert_mentions(msg["text"], get_username_func),
        )
        for msg in message_history
    ]
    messages.sort(key=lambda m: m[0])
    chatlog = [
        f"{ts.strftime('%H:%M:%S')} {userid}: {text}{stop_token}"
        for ts, userid, text in messages
    ]
    now = dt.now().strftime("%H:%M:%S")
    chatlog.append(f"{now} {bot_username}:")
    prompt = "\n".join(chatlog)
    gpt3_reply = get_gpt3_completion(prompt, stop_token)
    return gpt3_reply


def convert_mentions(text, get_username_func):
    regex = re.compile(r"<@(U[0-9A-Z]+)>")
    res = text
    while True:
        match = regex.search(res)
        if match:
            username = get_username_func(match.group(1))
            res = res[: match.start()] + f"@{username}" + res[match.end() :]
        else:
            break
    return res


if __name__ == "__main__":
    app.start(port=os.environ.get("SLACK_PORT", 3000))
