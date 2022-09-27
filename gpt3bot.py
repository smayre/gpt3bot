#!/usr/bin/python3

import os
from slack_bolt import App
from gpt3wrapper import generate_reply
import json

BOT_USERID = os.environ["SLACK_BOT_ID"]


app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


def block(type, **kwargs):
    return {"type": type, **kwargs}


def section(*args, **kwargs):
    return block(text=block(*args, **kwargs), type="section")


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        blocks = [
            section("mrkdwn", text="*GPT-3 bot*"),
            block(type="divider"),
            section("mrkdwn", text="WIP"),
            block(
                type="actions",
                elements=[
                    block(
                        type="button", text=block(type="plain_text", text="Do nothing")
                    )
                ],
            ),
        ]
        client.views_publish(
            user_id=event["user"],
            view=dict(
                type="home",
                callback_id="home_view",
                blocks=blocks,
            ),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
        logger.error(json.dumps(blocks, indent=4))


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
