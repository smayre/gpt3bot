import os
import sqlite3
from datetime import datetime as dt
from datetime import timedelta
import sys


USAGE_LOG = os.environ.get("USAGE_LOG", "/tmp/usage.db")

# cost per 1k tokens, USD
PRICING = {
    "text-ada-001": 0.0004,
    "text-babbage-001": 0.0005,
    "text-curie-001": 0.002,
    "text-davinci-003": 0.02,
    "gpt-3.5-turbo": 0.002,
    "gpt-4": 0.06
}


def set_up_usage_log(path):
    conn = sqlite3.connect(path)
    conn.execute("create table pricing (model text primary key, rate real)")
    conn.execute(
        "create table usage ("
        "    ts real primary key,"
        "    tokens integer,"
        "    model text references pricing (model))"
    )
    conn.execute(
        "create view costs as "
        "   select u.*, p.rate * (u.tokens/1000.0) as cost"
        "   from usage u left join pricing p"
        "   on u.model = p.model"
    )
    for m, p in PRICING.items():
        conn.execute("insert into pricing values (?, ?)", [m, p])
    conn.commit()
    conn.close()


def log_usage(ts, tokens, model, logfile=USAGE_LOG):
    conn = sqlite3.connect(logfile)
    conn.execute("PRAGMA foreign_keys = 1")
    conn.execute("insert into usage values (?, ?, ?)", [ts, tokens, model])
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
        "select * from costs where ts > ? order by 1", [start]
    )
    for ts, tokens, model, cost in cursor:
        ts_str = dt.fromtimestamp(ts).strftime("%d-%b-%Y %H:%M:%S").upper()
        print(f"{ts_str}: ${cost} ({tokens}/{model})")
    print(f"${get_cost(start)}")
