#!/usr/bin/python3

import os
from slack_bolt import App
from gpt3wrapper import get_gpt3_completion
from datetime import datetime as dt


BOT_USERID = os.environ["SLACK_BOT_ID"]
STOP_TOKEN = "<EOT>"
MESSAGE_LIMIT = 15


app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


@app.event("app_mention")
def reply_to_mention(logger, client, event, say):
    try:
        resp = client.conversations_history(
            channel=event["channel"], limit=MESSAGE_LIMIT
        )
        reply = generate_reply(resp["messages"], bot_userid=BOT_USERID)
        say(reply)
    except Exception as e:
        logger.error(e)
        raise


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
    messages.sort(key=lambda m: m[0])
    chatlog = [
        f"{ts.strftime('%H:%M:%S')} {userid}: {text}{stop_token}"
        for ts, userid, text in messages
    ]
    now = dt.now().isoformat()
    chatlog.append(f"{now} {bot_userid}:")
    prompt = "\n".join(chatlog)
    gpt3_reply = get_gpt3_completion(prompt, stop_token)
    return gpt3_reply


if __name__ == "__main__":
    app.start(port=os.environ.get("SLACK_PORT", 3000))
