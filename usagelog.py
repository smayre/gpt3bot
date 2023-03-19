import os
import sqlite3
from datetime import datetime as dt
from datetime import timedelta
import sys


USAGE_LOG = os.environ.get("USAGE_LOG", "/tmp/usage.db")

# cost per 1k tokens, USD
# model: (prompt_token_cost, completion_token_cost)
PRICING = {"gpt-3.5-turbo": (0.002,) * 2, "gpt-4": (0.03, 0.06)}


def set_up_usage_log(path):
    conn = sqlite3.connect(path)
    conn.execute(
        "create table pricing ("
        "    model text primary key, prompt_rate real, completion_rate real)"
    )
    conn.execute(
        "create table usage ("
        "    ts real primary key,"
        "    prompt_tokens integer,"
        "    completion_tokens integer,"
        "    model text references pricing (model))"
    )
    conn.execute(
        "create view costs as "
        "   select"
        "       u.*,"
        "       p.prompt_rate * (u.prompt_tokens/1000.0)"
        "           + p.completion_rate * (u.completion_tokens/1000.0)"
        "       as cost"
        "   from usage u left join pricing p"
        "   on u.model = p.model"
    )
    for m, (p, c) in PRICING.items():
        conn.execute("insert into pricing values (?, ?, ?)", [m, p, c])
    conn.commit()
    conn.close()


def log_usage(ts, usage, model, logfile=USAGE_LOG):
    prompt_tokens = usage["prompt_tokens"]
    completion_tokens = usage["completion_tokens"]
    conn = sqlite3.connect(logfile)
    conn.execute("PRAGMA foreign_keys = 1")
    conn.execute(
        "insert into usage values (?, ?, ?, ?)",
        [ts, prompt_tokens, completion_tokens, model],
    )
    conn.commit()
    conn.close()


def get_cost(start=0, logfile=USAGE_LOG):
    conn = sqlite3.connect(logfile)
    ((res,),) = conn.execute(
        "select sum(cost) from costs where ts > ?", [start]
    )
    return res or 0


if not os.path.exists(USAGE_LOG):
    try:
        set_up_usage_log(USAGE_LOG)
    except BaseException:
        os.remove(USAGE_LOG)
        raise
else:
    assert os.path.isfile(USAGE_LOG)


if __name__ == "__main__":
    try:
        hours = int(sys.argv[1])
    except IndexError:
        hours = 24
    start = (dt.now() - timedelta(hours=hours)).timestamp()
    conn = sqlite3.connect(USAGE_LOG)
    cursor = conn.execute(
        "select ts, model, cost from costs where ts > ? order by 1", [start]
    )
    for ts, model, cost in cursor:
        ts_str = dt.fromtimestamp(ts).strftime("%d-%b-%Y %H:%M:%S").upper()
        print(f"{ts_str}: ${cost} ({model})")
    print(f"${get_cost(start)}")
