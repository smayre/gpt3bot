#!/usr/bin/python3

import os
from slack_bolt import App
from gpt3wrapper import get_gpt3_completion
from datetime import datetime as dt


STOP_TOKEN = "<EOT>"
MESSAGE_LIMIT = 10
BOT_USERNAME = "gpt3bot"

CUTOFF = dt(*dt.today().timetuple()[:3]).timestamp()


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
            channel=event["channel"], limit=MESSAGE_LIMIT, oldest=CUTOFF
        )
        reply = generate_reply(resp["messages"], bot_username, user_map)
        say(reply)
    except Exception as e:
        logger.error(e)
        raise


@app.command("/gpt3-robotomy")
def set_cutoff(ack, command, say):
    print(f"{command['command']} {command['user_name']}")
    ack()
    say("I have been robotomised")
    global CUTOFF
    CUTOFF = dt.now().timestamp()


@app.command("/gpt3-say")
def say_something(ack, logger, client, command, say):
    print(f"{command['command']} {command['user_name']}")
    ack()
    event = dict(channel=command["channel_id"])
    reply_to_mention(logger, client, event, say)


def generate_reply(
    message_history, bot_username, user_map, stop_token=STOP_TOKEN
):
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
    return reconvert_mentions(gpt3_reply, user_map)


def convert_mentions(text, usermap):
    res = text
    for id, username in usermap.items():
        at_str = f"<@{id}>"
        while at_str in res:
            i = res.index(at_str)
            res = res[:i] + f"@{username}" + res[i + len(at_str) :]
    return res


def reconvert_mentions(text, usermap):
    res = text
    for id, username in usermap.items():
        at_str = f"@{username}"
        while at_str in res:
            i = res.index(at_str)
            res = res[:i] + f"<@{id}>" + res[i + len(at_str) :]
    return res


def get_user_map(client):
    resp = client.users_list()
    members = ((u["id"], u["name"]) for u in resp["members"])
    res = {id: name for id, name in members}
    return res


if __name__ == "__main__":
    app.start(port=os.environ.get("SLACK_PORT", 3000))
