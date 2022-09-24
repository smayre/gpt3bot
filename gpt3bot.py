#!/usr/bin/python3

import os
from slack_bolt import App


app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


if __name__ == "__main__":
    app.start(port=os.environ.get("SLACK_PORT", 3000))
