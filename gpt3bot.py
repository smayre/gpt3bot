#!/usr/bin/python3

import os
from slack_bolt import App
from gpt3wrapper import get_gpt3_completion
from datetime import datetime as dt
import re
import logging
import json


STOP_TOKEN = "<EOT>"
MESSAGE_LIMIT = 30
BOT_USERNAME = "gpt3bot"

CUTOFF = dt(*dt.today().timetuple()[:3]).timestamp()

PROMPT = []


logging.basicConfig(level=logging.INFO)


app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


@app.event("app_mention")
def reply_to_mention(logger, client, event, say):
    try:
        user_map = get_user_map(client)
        bot_username = BOT_USERNAME

        resp = client.conversations_history(
            channel=event["channel"], limit=MESSAGE_LIMIT
        )
        reply = generate_reply(
            resp["messages"], bot_username, user_map, logger
        )
        say(reply)
    except Exception as e:
        logger.error(e)
        raise


@app.command("/gpt3-robotomy")
def set_cutoff(ack, command, logger, say):
    logger.info(f"{command['command']} {command['user_name']}")
    ack()
    say("I have been robotomised")
    global CUTOFF
    CUTOFF = dt.now().timestamp()


@app.command("/gpt3-say")
def say_something(ack, logger, client, command, say):
    logger.info(f"{command['command']} {command['user_name']}")
    ack()
    event = dict(channel=command["channel_id"])
    reply_to_mention(logger, client, event, say)


def generate_reply(message_history, bot_username, user_map, logger):
    """Create a prompt for GPT-3 by converting a Slack conversation
    history into a chat log. Append the STOP_TOKEN to the end of each
    message so that (hopefully) GPT-3 will do the same, which we then
    use to cut off GPT-3's completion. Otherwise GPT-3 may produce a fake
    conversation with itself."""

    messages = [
        (
            dt.fromtimestamp(float(msg["ts"])),
            user_map[msg["user"]],
            convert_mentions(msg["text"], user_map),
        )
        for msg in message_history
        if float(msg["ts"]) > CUTOFF
    ]
    messages.sort(key=lambda m: m[0])
    chatlog = [
        {
            "role": "system",
            "content": "\n".join(PROMPT)
        }
    ]
    chatlog.extend(
        {
            "role": "assistant" if userid == BOT_USERNAME else "user",
            "content": f"{ts.strftime('%H:%M:%S')} {userid}: {text}",
        }
        for ts, userid, text in messages
    )
    logger.info(json.dumps(chatlog, indent=2))
    gpt3_reply = get_gpt3_completion(chatlog)
    gpt3_reply = remove_message_prefix(gpt3_reply)
    logger.info(gpt3_reply)
    return reconvert_mentions(gpt3_reply, user_map)


def convert_mentions(text, usermap):
    regex = re.compile(r"<@(U[A-Z0-9]+)>")
    res = regex.sub(lambda m: f"@{usermap.get(m.group(1), m.group(0))}", text)
    return res


def reconvert_mentions(text, usermap):
    res = text
    for uid, uname in usermap.items():
        res = re.sub(f"@{uname}", f"<@{uid}>", res)
    return res


def get_user_map(client):
    user_map = {}
    try:
        user_map = json.loads(open("user_map.json").read())
    except FileNotFoundError:
        resp = client.users_list()
        members = ((u["id"], u["name"]) for u in resp["members"])
        user_map = {id: name for id, name in members}
        with open("user_map.json", "w") as f:
            json.dump(user_map, f)
    return user_map


def remove_message_prefix(message):
    res = re.sub(r"\d\d:\d\d:\d\d [^:]+: (.*)$", lambda m: m.group(1), message)
    return res


if __name__ == "__main__":
    app.start(port=os.environ.get("SLACK_PORT", 3000))
