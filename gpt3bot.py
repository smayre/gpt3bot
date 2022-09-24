#!/usr/bin/python3

import os
from slack_bolt import App
import json


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


if __name__ == "__main__":
    app.start(port=os.environ.get("SLACK_PORT", 3000))
