#!/usr/bin/env python3
"""Queue manager for the DCF sweep (v5, 2026-10-13 — replaces hand-edited queue.json).

Usage:
  python3 queue.py [--file PATH] claim          -> print the claimed ticker
  python3 queue.py [--file PATH] done <TICKER>
  python3 queue.py [--file PATH] block <TICKER> [reason...]
  python3 queue.py [--file PATH] block <TICKER> --stdin   (reason read from stdin)
  python3 queue.py [--file PATH] reap            -> print reaped tickers
  python3 queue.py [--file PATH] requeue <TICKER>   (blocked/expired -> pending)
  python3 queue.py [--file PATH] migrate-data-gap   (one-off status migration)
  python3 queue.py pass2-claim                      -> print the second-pass ticker (v5.4)
  python3 queue.py pass2-done <TICKER> <done_no_change|done_changed>
  python3 queue.py pass2-reset <TICKER>             (-> pending)

All read-modify-write cycles run under an fcntl lock on <queue>.lock and are
saved atomically (tmp file + rename), so parallel workers can never claim the
same ticker or clobber each other's updates. claim stamps claimed_at (ET) and
runs the reaper first, under the same lock (round-2 audit: no job ever called
reap, so a crashed claim stayed in progress forever). block auto-selects the
status: a reason starting with "DATA_GAP" lands in blocked_data_gap (the list
awaiting override decisions), anything else in blocked_no_data. Reasons should
arrive via --stdin: a quoted shell argument mangles dollar amounts and quotes
(TKO's note lost the digits after each "$").
The queue.json schema is unchanged: {built, cutoff_market_cap_b, universe_size,
queue: [{ticker, queue_pos, status, ...}]}.
"""
import json, os, sys, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lock import locked  # v5.4: cross-platform exclusive file lock (fcntl / msvcrt)

ET = ZoneInfo("America/New_York")
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # v5.4
DEFAULT_FILE = f"{BASE}/_system/queue.json"
PASS2_FILE = f"{BASE}/_system/second_pass_queue.json"
LEASE_MINUTES = 90


def now_et():
    return datetime.datetime.now(ET)


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def with_lock(path, fn):
    with locked(f"{path}.lock"):
        data = load(path)
        result = fn(data)
        save(path, data)
        return result


# ---- v5.4: the second-pass queue goes through the same lock (the pass-2
# spec had workers hand-rewriting second_pass_queue.json as their "lock").
def _pass2_load(path):
    try:
        return load(path)
    except Exception:
        return {"entries": {}}


def cmd_pass2_claim(path, queue_path):
    """First candidate in queue order whose folder has a score.json and whose
    second-pass entry is absent or pending; marks it in_progress under the lock."""
    with locked(f"{path}.lock"):
        data = _pass2_load(path)
        entries = data.setdefault("entries", {})
        q = load(queue_path)
        cands = [e["ticker"] for e in q["queue"] if e.get("status") == "done"]
        if "APP" not in cands:
            cands.append("APP")  # the pilot sits outside the queue
        for t in cands:
            if not os.path.exists(f"{BASE}/{t}/score.json"):
                continue
            st = (entries.get(t) or {}).get("status")
            if st in (None, "pending"):
                entries[t] = {"status": "in_progress", "date": now_et().date().isoformat(),
                              "claimed_at": now_et().isoformat(timespec="seconds")}
                save(path, data)
                print(t)
                return
    print("queue.py: no pending second-pass candidates", file=sys.stderr)
    sys.exit(1)


def cmd_pass2_done(path, ticker, status):
    if status not in ("done_no_change", "done_changed", "pending"):
        print("queue.py: pass2-done status must be done_no_change | done_changed | pending", file=sys.stderr)
        sys.exit(2)
    with locked(f"{path}.lock"):
        data = _pass2_load(path)
        data.setdefault("entries", {})[ticker] = {"status": status, "date": now_et().date().isoformat()}
        save(path, data)
    print(f"{ticker} {status}")


def find(data, ticker):
    for e in data["queue"]:
        if e["ticker"] == ticker:
            return e
    return None


def _reap_locked(data):
    """Expired leases -> pending. Caller holds the lock. Returns reaped tickers."""
    cutoff = now_et() - datetime.timedelta(minutes=LEASE_MINUTES)
    reaped = []
    for e in data["queue"]:
        if e["status"] != "in_progress":
            continue
        claimed = e.get("claimed_at")
        stale = True  # pre-lease entries carry no claimed_at: always stale
        if claimed:
            try:
                stale = datetime.datetime.fromisoformat(claimed) < cutoff
            except ValueError:
                stale = True
        if stale:
            e["status"] = "pending"
            e.pop("claimed_at", None)
            reaped.append(e["ticker"])
    return reaped


def cmd_claim(path):
    def fn(data):
        _reap_locked(data)  # a crashed claim must not hold its ticker forever
        for e in data["queue"]:
            if e["status"] == "pending":
                e["status"] = "in_progress"
                e["claimed_at"] = now_et().isoformat(timespec="seconds")
                return e["ticker"]
        return None
    ticker = with_lock(path, fn)
    if ticker is None:
        print("queue.py: no pending entries", file=sys.stderr)
        sys.exit(1)
    print(ticker)


def cmd_done(path, ticker):
    def fn(data):
        e = find(data, ticker)
        if e is None:
            print(f"queue.py: {ticker} not in queue", file=sys.stderr)
            sys.exit(1)
        e["status"] = "done"
        e["completed"] = now_et().date().isoformat()
        return ticker
    with_lock(path, fn)
    print(f"{ticker} done")


def cmd_block(path, ticker, reason):
    # DATA_GAP blocks await a judgment decision (an override or a system fix);
    # NO_DATA blocks await filings that do not exist yet. Two lists, two statuses.
    status = "blocked_data_gap" if (reason or "").lstrip().upper().startswith("DATA_GAP") else "blocked_no_data"

    def fn(data):
        e = find(data, ticker)
        if e is None:
            print(f"queue.py: {ticker} not in queue", file=sys.stderr)
            sys.exit(1)
        e["status"] = status
        e["blocked_date"] = now_et().date().isoformat()
        if reason:
            e["note"] = f"{e['note']} | {reason}" if e.get("note") else reason
        return ticker
    with_lock(path, fn)
    print(f"{ticker} blocked ({status})")


def cmd_requeue(path, ticker):
    def fn(data):
        e = find(data, ticker)
        if e is None:
            print(f"queue.py: {ticker} not in queue", file=sys.stderr)
            sys.exit(1)
        if e["status"] not in ("blocked_no_data", "blocked_data_gap", "in_progress"):
            print(f"queue.py: {ticker} is {e['status']} — only blocked or in-progress entries requeue", file=sys.stderr)
            sys.exit(1)
        e["status"] = "pending"
        e.pop("claimed_at", None)
        return ticker
    with_lock(path, fn)
    print(f"{ticker} requeued (pending)")


def cmd_migrate_data_gap(path):
    """One-off (round-2): entries blocked before the blocked_data_gap status
    existed, whose note carries a DATA_GAP reason, move to the new status."""
    def fn(data):
        moved = []
        for e in data["queue"]:
            if e["status"] == "blocked_no_data" and (e.get("note") or "").lstrip().upper().startswith("DATA_GAP"):
                e["status"] = "blocked_data_gap"
                moved.append(e["ticker"])
        return moved
    for t in with_lock(path, fn):
        print(t)


def cmd_reap(path):
    for t in with_lock(path, _reap_locked):
        print(t)


def main():
    args = sys.argv[1:]
    path = DEFAULT_FILE
    if "--file" in args:
        i = args.index("--file")
        path = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args:
        print(__doc__)
        sys.exit(2)
    cmd, rest = args[0], args[1:]
    if cmd == "claim":
        cmd_claim(path)
    elif cmd == "done" and len(rest) == 1:
        cmd_done(path, rest[0].upper())
    elif cmd == "block" and len(rest) >= 1:
        if rest[1:] == ["--stdin"]:
            cmd_block(path, rest[0].upper(), sys.stdin.read().strip())
        else:
            cmd_block(path, rest[0].upper(), " ".join(rest[1:]))
    elif cmd == "requeue" and len(rest) == 1:
        cmd_requeue(path, rest[0].upper())
    elif cmd == "migrate-data-gap":
        cmd_migrate_data_gap(path)
    elif cmd == "reap":
        cmd_reap(path)
    elif cmd == "pass2-claim":
        cmd_pass2_claim(PASS2_FILE, path)
    elif cmd == "pass2-done" and len(rest) == 2:
        cmd_pass2_done(PASS2_FILE, rest[0].upper(), rest[1])
    elif cmd == "pass2-reset" and len(rest) == 1:
        cmd_pass2_done(PASS2_FILE, rest[0].upper(), "pending")
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
