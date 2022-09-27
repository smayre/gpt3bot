#!/usr/bin/python3

import os
from slack_bolt import App
from gpt3wrapper import generate_reply

BOT_USERID = os.environ["SLACK_BOT_ID"]


app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


@app.event("app_mention")
def reply_to_mention(logger, client, event, say):
    try:
        resp = client.conversations_history(
            channel=event["channel"],
            limit=75
        )
        reply = generate_reply(resp["messages"], bot_userid=BOT_USERID)
        say(reply)
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    app.start(port=os.environ.get("SLACK_PORT", 3000))
